from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from config import database_configuration
from database.base_model import BaseModel


class VerificationCode(BaseModel):
    __tablename__ = 'verification_codes'
    __database__ = database_configuration

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(unique=True)
    encode_id: Mapped[str] = mapped_column(nullable=True, unique=True)
    code: Mapped[str] = mapped_column(String(6))
    activate: Mapped[bool] = mapped_column(default=False)
