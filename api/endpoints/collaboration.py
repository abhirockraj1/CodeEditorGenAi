from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import SecurityScopes
import json
from jose import jwt
from ..core.config import settings

from ..core.dependencies import get_db, get_current_active_user, get_owner_or_collaborator
from ..utils.websocket_manager import manager
from api import models as pydantic_models
from api import schemas as db_schemas  # Correct import for database schemas
from ..services import code_file_service, user_service

router = APIRouter(prefix="/collaboration", tags=["collaboration"])

async def get_websocket_user(websocket: WebSocket, db: Session = Depends(get_db)):
    try:
        token = websocket.query_params.get("token")
        if not token:
            raise HTTPException(status_code=status.WS_1008_POLICY_VIOLATION, detail="Authentication token not provided")
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=status.WS_1008_POLICY_VIOLATION, detail="Invalid token payload")
        user = user_service.get_user(db, user_id=user_id)
        if user is None:
            raise HTTPException(status_code=status.WS_1008_POLICY_VIOLATION, detail="User not found")
        return user
    except Exception as e:
        print(f"WebSocket authentication error: {e}")
        raise HTTPException(status_code=status.WS_1008_POLICY_VIOLATION, detail="Invalid authentication credentials")


@router.websocket("/ws/{file_id}")
async def websocket_endpoint(websocket: WebSocket, file_id: int, current_user: db_schemas.User = Depends(get_websocket_user), db: Session = Depends(get_db)):
    
    code_file = code_file_service.get_code_file(db, file_id=file_id)
    if not code_file or (code_file.owner_id != current_user.id and current_user not in code_file.collaborators):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    user_id = current_user.id
    await manager.connect(websocket, file_id, user_id)
    # await websocket.accept() # Accept the connection AFTER dependencies are resolved
    await manager.broadcast({"type": "user_joined", "user_id": user_id, "email": current_user.email}, file_id, exclude_user_id=user_id)

    # Send the current file content to the newly joined user
    await manager.send_personal_message({"type": "initial_content", "content": code_file.content}, websocket)

    try:
        while True:
            data = await websocket.receive_json()
            data["user_id"] = user_id
            data["file_id"] = file_id

            message_type = data.get("type")

            if message_type == "text_change":
                change = pydantic_models.TextChange(**data)
                # Simple "last write wins" for content update
                db_file = code_file_service.get_code_file(db, file_id=file_id)
                if db_file:
                    content = list(db_file.content)
                    content[change.start:change.start + change.delete_count] = list(change.insert)
                    code_file_service.update_code_file(db, file_id=file_id, file=pydantic_models.CodeFileUpdate(content="".join(content)))
                    # Broadcast the change to other connected users
                    await manager.broadcast(data, file_id, exclude_user_id=user_id)
            elif message_type == "cursor_position":
                cursor_data = pydantic_models.CursorPosition(**data)
                await manager.broadcast(data, file_id, exclude_user_id=user_id)
            elif message_type == "highlight":
                highlight_data = pydantic_models.Highlight(**data)
                await manager.broadcast(data, file_id, exclude_user_id=user_id)
            else:
                print(f"Received unknown message type: {message_type}")

    except WebSocketDisconnect:
        manager.disconnect(file_id, user_id)
        await manager.broadcast({"type": "user_left", "user_id": user_id}, file_id)
    except Exception as e:
        print(f"WebSocket error for user {user_id} in file {file_id}: {e}")
        manager.disconnect(file_id, user_id)
        await manager.broadcast({"type": "user_left", "user_id": user_id}, file_id)

@router.post("/{file_id}/add_collaborator", response_model=pydantic_models.CodeFile)
def add_collaborator_to_file(
    file_id: int,
    collaborator: db_schemas.AddCollaborator,
    db: Session = Depends(get_db),
    current_user: db_schemas.User = Depends(get_current_active_user),
):
    db_file = code_file_service.get_code_file(db, file_id=file_id)
    if not db_file or db_file.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the owner can add collaborators")
    updated_file = code_file_service.add_collaborator(db, file_id=file_id, user_email=collaborator.email)
    if not updated_file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collaborator user not found")
    return updated_file

@router.post("/{file_id}/remove_collaborator", response_model=pydantic_models.CodeFile)
def remove_collaborator_from_file(
    file_id: int,
    collaborator: db_schemas.RemoveCollaborator,
    db: Session = Depends(get_db),
    current_user: db_schemas.User = Depends(get_current_active_user),
):
    db_file = code_file_service.get_code_file(db, file_id=file_id)
    if not db_file or db_file.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the owner can remove collaborators")
    user_to_remove = user_service.get_user(db, user_id=collaborator.user_id)
    if not user_to_remove or user_to_remove not in db_file.collaborators:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collaborator not found in this file")
    db_file.collaborators.remove(user_to_remove)
    db.commit()
    db.refresh(db_file)
    return db_file