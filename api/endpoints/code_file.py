from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api import models as pydantic_models
from api import schemas as db_schemas
from ..core.dependencies import get_db, get_current_active_user, get_owner_or_collaborator
from ..services import code_file_service

router = APIRouter(prefix="/files", tags=["code_files"])

@router.post("/", response_model=pydantic_models.CodeFile, status_code=status.HTTP_201_CREATED)
def create_file(file: pydantic_models.CodeFileCreate, db: Session = Depends(get_db), current_user: db_schemas.User = Depends(get_current_active_user)):
    return code_file_service.create_code_file(db, file=file, owner_id=current_user.id)

@router.get("/{file_id}", response_model=pydantic_models.CodeFile)
def read_file(file: db_schemas.CodeFile = Depends(get_owner_or_collaborator)):
    return file

@router.put("/{file_id}", response_model=pydantic_models.CodeFile)
def update_file(
    file_id: int,
    file_update: pydantic_models.CodeFileUpdate,
    db: Session = Depends(get_db),
    current_user: db_schemas.User = Depends(get_current_active_user),
):
    db_file = code_file_service.get_code_file(db, file_id=file_id)
    if not db_file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Code file not found")
    if db_file.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this file")
    return code_file_service.update_code_file(db, file_id=file_id, file=file_update)

@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: db_schemas.User = Depends(get_current_active_user),
):
    db_file = code_file_service.get_code_file(db, file_id=file_id)
    if not db_file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Code file not found")
    if db_file.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this file")
    if code_file_service.delete_code_file(db, file_id=file_id):
        return
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete file")

# Add endpoints for listing user's files, etc.