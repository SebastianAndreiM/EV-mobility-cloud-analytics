"""Shared FastAPI dependencies (current user from JWT)."""
import jwt
from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.exceptions import UnauthorizedError
from app.core.security import decode_access_token
from app.services.auth_service import AuthService

_bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
):
    if credentials is None:
        raise UnauthorizedError("Not authenticated")
    try:
        payload = decode_access_token(credentials.credentials)
        user_id = int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        raise UnauthorizedError("Invalid token")
    request.state.user_id = user_id
    user = await AuthService().get_user(user_id)
    return user
