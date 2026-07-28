from fastapi import APIRouter
from app.db.session import check_db_connection

router = APIRouter()

@router.get("/health")
def health_check():
    db_status = "connected" if check_db_connection() else "disconnected"
    return {"status": "healthy", "db": db_status}
