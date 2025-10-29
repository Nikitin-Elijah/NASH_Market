from typing import List

from sqlalchemy import String, DECIMAL, ForeignKey, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.config import database_configuration
from src.database.base_model import BaseModel


class ProductModel(BaseModel):
    __tablename__ = 'products'
    __database__ = database_configuration

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    price: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
    seller_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.id'), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)

    seller: Mapped['UserModel'] = relationship('UserModel', back_populates='products')
    images: Mapped[List['ImageModel']] = relationship(
        'ImageModel',
        back_populates='product',
        uselist=True,
        cascade='all, delete-orphan'
    )
    purchases: Mapped[List['PurchaseModel']] = relationship(
        'PurchaseModel',
        back_populates='product',
        uselist=True,
        cascade='all, delete-orphan'
    )
    favorited_by: Mapped[List['UserFavoriteModel']] = relationship(
        'UserFavoriteModel',
        back_populates='product',
        uselist=True,
        cascade='all, delete-orphan'
    )