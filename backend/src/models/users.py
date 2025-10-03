from typing import List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.config import database_configuration
from src.database.base_model import BaseModel


class UserModel(BaseModel):
    __tablename__ = 'users'
    __database__ = database_configuration

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(nullable=False, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    photo_url: Mapped[str | None] = mapped_column(default=None)

    products: Mapped[List['ProductModel']] = relationship('ProductModel', back_populates='seller', uselist=True)

    def __str__(self):
        return f'{self.id=}, {self.username=}'
