from fastapi import FastAPI,Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from .endpoints import user, code_file, collaboration
from .core.database import Base, engine
from api.models import ai_debugging as ai_debugging_models
from api.services import ai_debugging_service
Base.metadata.create_all(bind=engine)

app = FastAPI()
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

async def rate_limit_exception_handler(request: Request, exc: RateLimitExceeded):
    return HTTPException(
        status_code=429,
        detail=f"Rate limit exceeded. Try again in {exc.retry_after} seconds.",
    )
app.add_exception_handler(RateLimitExceeded, rate_limit_exception_handler)

# Kept the ai suggestion route in main.py because slowapi libary was not handling the sub routers for rate limiting correctly.
@app.post("/ai_debugging/analyze_code", response_model=ai_debugging_models.CodeAnalysisResponse)
@limiter.limit("5/minute")  # This endpoint will be rate-limited to a maximum of 5 requests per minute from the same client.
async def analyze_code(
    request: Request, 
    code_analysis_request: ai_debugging_models.CodeAnalysisRequest,
    ai_service: ai_debugging_service.AIDebuggingService = Depends()
):
    """
    Analyzes the provided code using the OpenRouter AI model.
    """
    suggestions = await ai_service.analyze_code(code_analysis_request.code, code_analysis_request.language)
    return {"suggestions": suggestions}


origins = [
    "http://localhost",
    "http://localhost:8080",
    # Add other allowed origins here
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router)
app.include_router(code_file.router)
app.include_router(collaboration.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)