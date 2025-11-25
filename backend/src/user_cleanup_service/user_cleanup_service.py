from datetime import datetime, timedelta
import logging

from sqlalchemy import select

from src.database.database_config import DatabaseConfig
from src.models import UserModel


logger = logging.getLogger(__name__)


class UserCleanupService:
    def __init__(self, database: DatabaseConfig):
        self.database = database

    async def delete_unverified_users(self, hours_threshold: int = 1) -> int:
        """
        Удаляет пользователей, которые не подтвердили регистрацию в течение N часов
        """
        try:
            threshold_time = datetime.now() - timedelta(hours=hours_threshold)

            async with self.database.async_session_maker() as session:
                unverified_users = await session.scalars(
                    select(UserModel).where(
                        UserModel.is_active == False,
                        UserModel.created_at < threshold_time,
                    )
                )

            deleted_count = 0

            for user in unverified_users:
                logger.info(
                    f"Удаление неактивного пользователя: {user.username} (создан: {user.created_at})"
                )
                await user.delete()
                deleted_count += 1

            if deleted_count > 0:
                logger.info(f"Удалено {deleted_count} неактивных пользователей")

            else:
                logger.info("Неактивные пользователи для удаления не найдены")

            return deleted_count

        except Exception as e:
            logger.error(f"Ошибка при удалении неактивных пользователей: {str(e)}")
            raise
