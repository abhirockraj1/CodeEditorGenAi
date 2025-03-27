from typing import Dict, List
from fastapi import Depends
from api.ai_integration.ai_model import OpenRouterAIModel  
from api.core.config import settings  # To access OpenRouter API key, site URL, and name

class AIDebuggingService:
    def __init__(self, openrouter_model: OpenRouterAIModel = Depends()):
        self.openrouter_model = openrouter_model

    async def analyze_code(self, code: str, language: str) -> Dict[str, List[str]]:
        """
        Analyzes the provided code using the OpenRouter AI model and returns suggestions.
        """
        return await self.openrouter_model.analyze(code, language)