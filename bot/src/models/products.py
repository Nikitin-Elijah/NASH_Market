from typing import List

from sqlalchemy import String, DECIMAL, ForeignKey, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from config import database_configuration
from database.base_model import BaseModel


class ProductModel(BaseModel):
    __tablename__ = 'products'
    __database__ = database_configuration

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    price: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
    image_url: Mapped[str] = mapped_column(nullable=False)
    rating: Mapped[float] = mapped_column(default=0.0)
    seller_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.id'), nullable=False)

    seller: Mapped['UserModel'] = relationship('UserModel', back_populates='products')
    purchases: Mapped[List['PurchaseModel']] = relationship(
        'PurchaseModel',
        uselist=True,
        back_populates='product',
        cascade='all, delete-orphan'
    )