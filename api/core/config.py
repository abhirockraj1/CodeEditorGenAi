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