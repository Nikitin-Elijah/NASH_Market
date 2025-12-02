from sqlalchemy import ForeignKey, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.config import database_configuration
from src.database.base_model import BaseModel


class ImageModel(BaseModel):
    __tablename__ = "images"
    __database__ = database_configuration

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("products.id"), nullable=False
    )
    url: Mapped[str] = mapped_column(nullable=False)
    is_main: Mapped[bool] = mapped_column(default=False)

    product: Mapped["ProductModel"] = relationship(
        "ProductModel", back_populates="images"
    )
