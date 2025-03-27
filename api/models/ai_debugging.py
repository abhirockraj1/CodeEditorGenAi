from pydantic import BaseModel
from typing import Dict, List

class CodeAnalysisRequest(BaseModel):
    code: str
    language: str # 'python', 'javascript', etc.

class CodeAnalysisResponse(BaseModel):
    suggestions: Dict[str, List[str]]