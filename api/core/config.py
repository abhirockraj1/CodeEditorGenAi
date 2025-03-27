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