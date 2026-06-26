from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.patterns.repository import AsyncRepository


class UserRepository(AsyncRepository[User]):
    model = User

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_by_email(self, email: str) -> User | None:
        res = await self.session.execute(select(User).where(User.email == email))
        return res.scalar_one_or_none()
