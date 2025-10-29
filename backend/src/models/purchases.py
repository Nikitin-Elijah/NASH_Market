from datetime import datetime

from sqlalchemy import BigInteger, ForeignKey, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.config import database_configuration
from src.database.base_model import BaseModel


class PurchaseModel(BaseModel):
    __tablename__ = 'purchases'
    __database__ = database_configuration

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('products.id'), nullable=False)
    seller_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.id'), nullable=False)
    buyer_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.id'), nullable=False)
    comment: Mapped[int | None] = mapped_column(String(100), default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    permission: Mapped[bool] = mapped_column(default=False)
    refusal: Mapped[bool] = mapped_column(default=False)
    successful: Mapped[bool] = mapped_column(default=False)

    product: Mapped['ProductModel'] = relationship('ProductModel', back_populates='purchases')
    seller: Mapped['UserModel'] = relationship('UserModel', back_populates='offers', foreign_keys=[seller_id])
    buyer: Mapped['UserModel'] = relationship('UserModel', back_populates='purchases', foreign_keys=[buyer_id])
    review: Mapped['ReviewModel'] = relationship('ReviewModel', back_populates='purchase')

    def __repr__(self):
        attrs = {
            'id': self.id,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S.%f') if self.created_at else None,
            'permission': self.permission,
            'successful': self.successful,
            'product_id': self.product_id,
            'seller_id': self.seller_id,
            'buyer_id': self.buyer_id,
        }

        return "{" + ", ".join(f"{k}: {v}" for k, v in attrs.items()) + "}"