from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func, Table
from sqlalchemy.orm import relationship

from ..core.database import Base

class CodeFile(Base):
    __tablename__ = "code_files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    content = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    owner = relationship("User", back_populates="owned_files")
    collaborators = relationship("User", secondary="collaborations_table", back_populates="collaborations")
    editing_sessions = relationship("EditingSession", back_populates="code_file")

class EditingSession(Base):
    __tablename__ = "editing_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    file_id = Column(Integer, ForeignKey("code_files.id"))
    session_start = Column(DateTime, default=func.now())
    session_end = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="editing_sessions")
    code_file = relationship("CodeFile", back_populates="editing_sessions")