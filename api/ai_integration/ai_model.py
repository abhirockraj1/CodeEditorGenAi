from openai import OpenAI
from typing import Dict, List
from api.core.config import settings  # To access OpenRouter API key, site URL, and name
from fastapi import HTTPException

class OpenRouterAIModel:
    def __init__(self):
        """
        Initializes the OpenAI client for OpenRouter.
        """
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=settings.OPENROUTER_API_KEY,
        )
        self.model_name = "qwen/qwen-2.5-coder-32b-instruct:free"
        print("OpenRouter AI Model Initialized")

    async def analyze(self, code: str, language: str) -> Dict[str, List[str]]:
        """
        Sends the code to the OpenRouter AI model for analysis and returns suggestions.
        """
        prompt = f"""Please analyze the following code for:
- Syntax errors
- Potential bugs
- Performance improvement opportunities

```{language}
{code}
```"""

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful code analysis assistant."},
                    {"role": "user", "content": prompt}
                ]
            )

            # Extract the response content
            analysis_text = response.choices[0].message.content

            # Process the response into categories
            result = {
                "syntax_errors": [],
                "potential_bugs": [],
                "performance_improvements": []
            }

            # Simple parsing of the response (this could be improved with more sophisticated parsing)
            current_category = None
            for line in analysis_text.split('\n'):
                line = line.strip()
                if "syntax error" in line.lower() or "syntax errors" in line.lower():
                    current_category = "syntax_errors"
                    continue
                elif "bug" in line.lower() or "potential bug" in line.lower():
                    current_category = "potential_bugs"
                    continue
                elif "performance" in line.lower() or "improvement" in line.lower():
                    current_category = "performance_improvements"
                    continue

                if current_category and line and not line.startswith('#') and not line.startswith('-'):
                    result[current_category].append(line)

            return result

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error analyzing code: {str(e)}")