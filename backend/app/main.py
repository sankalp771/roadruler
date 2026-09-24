from fastapi import FastAPI
from app.api.routes import health, users, complaints, authority, analytics
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(health.router)
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(complaints.router, prefix="/api/v1/complaints", tags=["complaints"])
app.include_router(authority.router, prefix="/api/v1/authority", tags=["authority"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])

@app.get("/")
def read_root():
    return {"message": "Welcome to RoadRuler API"}
