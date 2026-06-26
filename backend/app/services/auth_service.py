import logging

from app.core.exceptions import ConflictError, UnauthorizedError
from app.core.logging_config import get_logger, log_event
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.patterns.unit_of_work import UnitOfWork

logger = get_logger("auth_service")


class AuthService:
    async def register(self, email: str, password: str, full_name: str | None) -> User:
        async with UnitOfWork() as uow:
            existing = await uow.users.get_by_email(email)
            if existing:
                raise ConflictError("Email already registered")
            user = User(email=email, hashed_password=hash_password(password), full_name=full_name)
            await uow.users.add(user)
            await uow.commit()
            await uow._session.refresh(user)
            log_event(logger, logging.INFO, "user_registered", user_id=user.id)
            return user

    async def login(self, email: str, password: str) -> str:
        async with UnitOfWork() as uow:
            user = await uow.users.get_by_email(email)
            if not user or not verify_password(password, user.hashed_password):
                raise UnauthorizedError("Invalid credentials")
            token = create_access_token(subject=user.id)
            log_event(logger, logging.INFO, "user_login", user_id=user.id)
            return token

    async def get_user(self, user_id: int) -> User:
        async with UnitOfWork() as uow:
            user = await uow.users.get(user_id)
            if not user:
                raise UnauthorizedError("User not found")
            return user
