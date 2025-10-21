from datetime import datetime, timedelta
import logging

from sqlalchemy import select

from src.database.database_config import DatabaseConfig
from src.models import UserModel

logger = logging.getLogger(__name__)


class UserCleanupService:
    def __init__(self, database: DatabaseConfig):
        self.database = database

    async def delete_unverified_users(self, hours_threshold: int = 24) -> int:
        """
        Удаляет пользователей, которые не подтвердили регистрацию в течение N часов
        """
        try:
            threshold_time = datetime.utcnow() - timedelta(hours=hours_threshold)

            async with self.database.async_session_maker() as session:
                unverified_users = await session.scalars(
                    select(UserModel).where(
                        UserModel.is_active == False,
                        UserModel.created_at < threshold_time
                    )
                )

            deleted_count = 0

            for user in unverified_users:
                logger.info(f"Удаление неактивного пользователя: {user.username} (создан: {user.created_at})")
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

    # def get_unverified_users_stats(self, hours_threshold: int = 24) -> dict:
    #     """
    #     Статистика по неактивным пользователям
    #     """
    #     threshold_time = datetime.utcnow() - timedelta(hours=hours_threshold)
    #
    #     total_unverified = self.db.query(UserModel).filter(
    #         UserModel.is_active == False,
    #         UserModel.created_at < threshold_time
    #     ).count()
    #
    #     # Пользователи по возрастным группам
    #     age_groups = {
    #         "24_48_hours": self.db.query(UserModel).filter(
    #             UserModel.is_active == False,
    #             UserModel.created_at < datetime.utcnow() - timedelta(hours=48),
    #             UserModel.created_at >= datetime.utcnow() - timedelta(hours=72)
    #         ).count(),
    #         "over_72_hours": self.db.query(UserModel).filter(
    #             UserModel.is_active == False,
    #             UserModel.created_at < datetime.utcnow() - timedelta(hours=72)
    #         ).count()
    #     }
    #
    #     return {
    #         "total_unverified": total_unverified,
    #         "age_groups": age_groups,
    #         "threshold_hours": hours_threshold
    #     }