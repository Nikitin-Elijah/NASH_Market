from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker


class DatabaseConfig:
    """
        Database configuration
    """
    def __init__(self, database_url: str) -> None:
        self.database_url: str = database_url
        self.async_engine = create_async_engine(self.database_url, echo=True)
        self.async_session_maker = async_sessionmaker(self.async_engine, expire_on_commit=False, class_=AsyncSession)

    async def get_async_session(self) -> AsyncSession:
        """
        Предоставляет асинхронную сессию SQLAlchemy для работы с базой данных PostgreSQL.
        """
        async with self.async_session_maker() as session:
            yield session
