from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from .config import settings
from .. import schemas as db_schemas
from .. import models as pydantic_models
from ..services import user_service, code_file_service
from .database import get_db  # Corrected import: relative import

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = pydantic_models.TokenData(id=user_id)
    except JWTError:
        raise credentials_exception
    user = user_service.get_user(db, user_id=token_data.id)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: db_schemas.User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user

async def get_owner_or_collaborator(file_id: int, current_user: db_schemas.User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    code_file = code_file_service.get_code_file(db, file_id=file_id)
    if not code_file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Code file not found")
    if code_file.owner_id != current_user.id and current_user not in code_file.collaborators:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this file")
    return code_file