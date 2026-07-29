from fastapi import FastAPI
from app.api.routes import health, users, complaints
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(health.router)
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(complaints.router, prefix="/api/v1/complaints", tags=["complaints"])

@app.get("/")
def read_root():
    return {"message": "Welcome to RoadRuler API"}
