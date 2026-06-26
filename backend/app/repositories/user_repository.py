"""Repository for accounts and their auth credentials."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import Account, AuthCredential
from app.patterns.repository import AsyncRepository


class UserRepository(AsyncRepository[Account]):
    model = Account

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_by_email(self, email: str) -> Account | None:
        res = await self.session.execute(
            select(Account).where(Account.email == email)
        )
        return res.scalar_one_or_none()

    async def get_credential(
        self, account_id: int, provider: str = "local"
    ) -> AuthCredential | None:
        res = await self.session.execute(
            select(AuthCredential).where(
                AuthCredential.account_id == account_id,
                AuthCredential.provider == provider,
            )
        )
        return res.scalar_one_or_none()

    async def add_credential(self, credential: AuthCredential) -> AuthCredential:
        self.session.add(credential)
        await self.session.flush()
        return credential