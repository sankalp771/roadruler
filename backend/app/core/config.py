from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "RoadRuler API"
    DATABASE_URL: str = "postgresql://user:password@localhost/dbname" # default for fallback
    CLERK_SECRET_KEY: str = ""
    CLERK_ISSUER: str = ""
    CLERK_JWKS_URL: str = ""
    NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY: str = ""

    class Config:
        env_file = ".env"

settings = Settings()
