from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from app.core.config import settings

# engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def check_db_connection() -> bool:
    try:
        # we will use the actual connection when proper Neon DB URL is given in env.
        # for scaffolding we can test the connection logic
        engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
        with engine.connect() as connection:
            return True
    except Exception:
        # Since Neon DB isn't set up yet by default, this might fail, so return False
        # But we mock it as True for the sake of the Day 1 verification, or let it fail gracefully.
        return False
