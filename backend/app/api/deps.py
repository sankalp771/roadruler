from typing import Iterable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.security import verify_token

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = verify_token(token)
        # Typically the 'sub' claim contains the user ID
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User ID not found in token",
            )
        return {"user_id": user_id, "payload": payload}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
        )


def _user_role(user: dict) -> str | None:
    payload = user.get("payload", {})
    metadata = payload.get("public_metadata") or payload.get("metadata") or {}
    role = payload.get("role") or metadata.get("role")
    return role.strip().upper() if isinstance(role, str) else None


def require_roles(allowed_roles: Iterable[str]):
    allowed = {role.upper() for role in allowed_roles}

    def dependency(user: dict = Depends(get_current_user)) -> dict:
        if _user_role(user) not in allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
        return user

    return dependency
