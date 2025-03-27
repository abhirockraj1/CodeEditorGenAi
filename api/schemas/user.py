from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from ..core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    owned_files = relationship("CodeFile", back_populates="owner")
    collaborations = relationship("CodeFile", secondary="collaborations_table", back_populates="collaborators")
    editing_sessions = relationship("EditingSession", back_populates="user")

class Collaboration(Base):
    __tablename__ = "collaborations_table"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    file_id = Column(Integer, ForeignKey("code_files.id"), primary_key=True)