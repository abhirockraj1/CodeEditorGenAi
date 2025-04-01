from pydantic_settings  import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:postgres@db:5432/Newdb"
    SECRET_KEY: str = "your_very_secret_key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    OPENROUTER_API_KEY: str = "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"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()