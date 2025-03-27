from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from api import models as pydantic_models  # Pydantic models for request/response
from api import schemas as db_schemas    # SQLAlchemy models for database
from ..core.dependencies import get_db, get_current_active_user
from ..services import user_service
from ..utils import security

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/register", response_model=pydantic_models.User, status_code=status.HTTP_201_CREATED)
def register_user(user: pydantic_models.UserCreate, db: Session = Depends(get_db)):
    db_user = user_service.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    return user_service.create_user(db, user=user)

@router.post("/login", response_model=pydantic_models.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = user_service.get_user_by_email(db, email=form_data.username)
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = security.timedelta(minutes=30) # token expire at 30 minutes
    access_token = security.create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=pydantic_models.User)
async def read_users_me(current_user: db_schemas.User = Depends(get_current_active_user)):
    return current_user
