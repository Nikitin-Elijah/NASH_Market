from datetime import datetime

from sqlalchemy import String, DateTime, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from config import database_configuration
from database.base_model import BaseModel


class UserModel(BaseModel):
    __tablename__ = 'users'
    __database__ = database_configuration

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    tg_user_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=True, default=None)
    tg_username: Mapped[str | None] = mapped_column(unique=True, nullable=True, default=None)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    photo_url: Mapped[str | None] = mapped_column(default=None)
    is_active: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
