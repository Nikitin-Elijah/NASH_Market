from datetime import datetime

from sqlalchemy import String, ForeignKey, BigInteger, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.config import database_configuration
from src.database.base_model import BaseModel


class ReviewModel(BaseModel):
    __tablename__ = 'reviews'
    __database__ = database_configuration

    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.id'), nullable=False)
    recipient_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.id'), nullable=False)
    purchase_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('purchases.id'), nullable=False)
    rating: Mapped[int] = mapped_column(nullable=False)
    text: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    author: Mapped['UserModel'] = relationship(
        'UserModel', back_populates='authored_reviews', foreign_keys=[author_id]
    )
    recipient: Mapped['UserModel'] = relationship(
        'UserModel', back_populates='received_reviews', foreign_keys=[recipient_id]
    )
    purchase: Mapped['PurchaseModel'] = relationship('PurchaseModel', back_populates='review')