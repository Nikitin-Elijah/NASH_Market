from sqlalchemy import String, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from config import database_configuration
from database.base_model import BaseModel


class VerificationCode(BaseModel):
    __tablename__ = 'verification_codes'
    __database__ = database_configuration

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    encode_id: Mapped[str] = mapped_column(nullable=True, unique=True)
    code: Mapped[str] = mapped_column(String(6))
    tg_user_id: Mapped[int | None] = mapped_column(BigInteger, default=None)
    tg_username: Mapped[str | None] = mapped_column(default=None)
    activate: Mapped[bool] = mapped_column(default=False)
