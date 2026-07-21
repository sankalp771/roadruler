from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "RoadRuler API"
    DATABASE_URL: str = "postgresql://user:password@localhost/dbname" # default for fallback

    class Config:
        env_file = ".env"

settings = Settings()
