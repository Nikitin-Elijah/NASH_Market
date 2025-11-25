from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.config import database_configuration
from src.database.base_model import BaseModel


class UserFavoriteModel(BaseModel):
    __tablename__ = "user_favorites"
    __database__ = database_configuration

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id"), nullable=False
    )
    product_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("products.id"), nullable=False
    )

    user: Mapped["UserModel"] = relationship("UserModel", back_populates="favorites")
    product: Mapped["ProductModel"] = relationship(
        "ProductModel", back_populates="favorited_by"
    )
