# No specific database model needed beyond the 'collaborations_table' in user.py
# This file might contain Pydantic models for collaboration-related requests/responses
from pydantic import BaseModel

class AddCollaborator(BaseModel):
    email: str

class RemoveCollaborator(BaseModel):
    user_id: int