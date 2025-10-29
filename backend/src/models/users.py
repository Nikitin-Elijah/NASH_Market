from datetime import datetime
from typing import List

from sqlalchemy import String, DateTime, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.config import database_configuration
from src.database.base_model import BaseModel


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
    rating: Mapped[float | None] = mapped_column(default=None)

    products: Mapped[List['ProductModel']] = relationship(
        'ProductModel',
        back_populates='seller',
        uselist=True,
        cascade='all, delete-orphan'
    )
    offers: Mapped[List['PurchaseModel']] = relationship(
        'PurchaseModel',
        back_populates='seller',
        uselist=True,
        cascade='all, delete-orphan',
        foreign_keys='PurchaseModel.seller_id'
    )
    purchases: Mapped[List['PurchaseModel']] = relationship(
        'PurchaseModel',
        back_populates='buyer',
        uselist=True,
        cascade='all, delete-orphan',
        foreign_keys='PurchaseModel.buyer_id'
    )
    authored_reviews: Mapped[List['ReviewModel']] = relationship(
        'ReviewModel',
        back_populates='author',
        uselist=True,
        cascade='all, delete-orphan',
        foreign_keys='ReviewModel.author_id'
    )
    received_reviews: Mapped[List['ReviewModel']] = relationship(
        'ReviewModel',
        back_populates='recipient',
        uselist=True,
        cascade='all, delete-orphan',
        foreign_keys='ReviewModel.recipient_id'
    )
    favorites: Mapped[List['UserFavoriteModel']] = relationship(
        'UserFavoriteModel',
        back_populates='user',
        uselist=True,
        cascade='all, delete-orphan'
    )

    def __str__(self):
        return f'{self.id=}, {self.username=}'
