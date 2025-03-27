from sqlalchemy.orm import Session
from api import models as pydantic_models  # Pydantic models for data validation
from api import schemas as db_schemas    # SQLAlchemy models for database interaction
from ..services import user_service

def get_code_file(db: Session, file_id: int):
    return db.query(db_schemas.CodeFile).filter(db_schemas.CodeFile.id == file_id).first()

def get_user_code_files(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(db_schemas.CodeFile).filter(db_schemas.CodeFile.owner_id == user_id).offset(skip).limit(limit).all()

def create_code_file(db: Session, file: pydantic_models.CodeFileCreate, owner_id: int):
    db_file = db_schemas.CodeFile(filename=file.filename, content="", owner_id=owner_id)
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file

def update_code_file(db: Session, file_id: int, file: pydantic_models.CodeFileUpdate):
    db_file = get_code_file(db, file_id=file_id)
    if db_file:
        for key, value in file.model_dump(exclude_unset=True).items():
            setattr(db_file, key, value)
        db.commit()
        db.refresh(db_file)
    return db_file

def delete_code_file(db: Session, file_id: int):
    db_file = get_code_file(db, file_id=file_id)
    if db_file:
        db.delete(db_file)
        db.commit()
        return True
    return False

def add_collaborator(db: Session, file_id: int, user_email: str):
    db_file = get_code_file(db, file_id=file_id)
    user = user_service.get_user_by_email(db, email=user_email)
    if db_file and user and user not in db_file.collaborators and db_file.owner_id != user.id:
        db_file.collaborators.append(user)
        db.commit()
        db.refresh(db_file)
        return db_file
    return None

def remove_collaborator(db: Session, file_id: int, collaborator_user_id: int):
    db_file = get_code_file(db, file_id=file_id)
    user_to_remove = user_service.get_user(db, user_id=collaborator_user_id)
    if db_file and user_to_remove and user_to_remove in db_file.collaborators:
        db_file.collaborators.remove(user_to_remove)
        db.commit()
        db.refresh(db_file)
        return db_file
    return None