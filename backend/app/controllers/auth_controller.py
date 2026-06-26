from fastapi import APIRouter, Depends, status

from app.core.deps import get_current_user
from app.core.rate_limit import RateLimiter
from app.schemas.auth_schema import (
    LoginRequest, RegisterRequest, TokenResponse, UserResponse,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])
_service = AuthService()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest):
    user = await _service.register(body.email, body.password, body.full_name)
    return user


@router.post("/login", response_model=TokenResponse,
             dependencies=[Depends(RateLimiter(times=5, seconds=60, scope="login"))])
async def login(body: LoginRequest):
    token = await _service.login(body.email, body.password)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
async def me(user=Depends(get_current_user)):
    return user
