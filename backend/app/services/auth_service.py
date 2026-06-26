import logging

from app.core.exceptions import ConflictError, UnauthorizedError
from app.core.logging_config import get_logger, log_event
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import Account, AuthCredential
from app.patterns.unit_of_work import UnitOfWork

logger = get_logger("auth_service")


class AuthService:
    async def register(
        self, email: str, password: str, full_name: str | None
    ) -> Account:
        """Create the identity (Account) and its local password credential as
        two separate rows within one transaction."""
        async with UnitOfWork() as uow:
            existing = await uow.users.get_by_email(email)
            if existing:
                raise ConflictError("Email already registered")

            account = Account(email=email, full_name=full_name)
            await uow.users.add(account)
            await uow._session.flush()  # assign account.id

            credential = AuthCredential(
                account_id=account.id,
                provider="local",
                hashed_password=hash_password(password),
            )
            await uow.users.add_credential(credential)

            await uow.commit()
            await uow._session.refresh(account)
            log_event(logger, logging.INFO, "account_registered", account_id=account.id)
            return account

    async def login(self, email: str, password: str) -> str:
        """Verify the local credential and issue a JWT carrying account_id."""
        async with UnitOfWork() as uow:
            account = await uow.users.get_by_email(email)
            if not account:
                raise UnauthorizedError("Invalid credentials")
            credential = await uow.users.get_credential(account.id, provider="local")
            if (
                not credential
                or not credential.hashed_password
                or not verify_password(password, credential.hashed_password)
            ):
                raise UnauthorizedError("Invalid credentials")
            token = create_access_token(subject=account.id)
            log_event(logger, logging.INFO, "account_login", account_id=account.id)
            return token

    async def get_user(self, account_id: int) -> Account:
        async with UnitOfWork() as uow:
            account = await uow.users.get(account_id)
            if not account:
                raise UnauthorizedError("Account not found")
            return account