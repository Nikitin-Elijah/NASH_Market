from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from src.config import database_configuration


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Предоставляет асинхронную сессию SQLAlchemy для работы с базой данных PostgreSQL.
    """
    async with database_configuration.async_session_maker() as session:
        yield session
