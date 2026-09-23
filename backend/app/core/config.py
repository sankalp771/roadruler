from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "RoadRuler API"
    DATABASE_URL: str = "postgresql://user:password@localhost/dbname" # default for fallback
    CLERK_SECRET_KEY: str = ""
    CLERK_ISSUER: str = ""
    CLERK_JWKS_URL: str = ""
    NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY: str = ""
    
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""

    REDIS_URL: str = "redis://localhost:6379/0"
    # Empty string -> ai_service prefers downloaded road_damage_v8s.pt, then best.pt.
    AI_WEIGHTS_PATH: str = ""

    class Config:
        env_file = ".env"

settings = Settings()
