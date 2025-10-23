from datetime import datetime

from pydantic import BaseModel, Field


class PurchaseCreate(BaseModel):
    """
    Модель для создания записи о покупке товара
    """
    product_id: int = Field(description='ID товара')
    comment: str | None = Field(max_length=100, default=None, description='Комментарий к покупке')


class PurchaseSchema(BaseModel):
    """
    Модель для ответа с данными о покупке товара
    """
    id: int = Field(description='ID покупки')
    product_id: int = Field(description='ID товара')
    seller_id: int = Field(description='ID продавца')
    buyer_id: int = Field(description='ID покупателя')
    comment: str | None = Field(max_length=100, default=None, description='Комментарий к покупке')
    created_at: datetime = Field(description='Дата и время создания записи о покупке')
    permission: bool = Field(description='Флаг - подтверждена ли покупка')
    refusal: bool = Field(description='Флаг - отклонена ли покупка')
    successful: bool = Field(description='Флаг - закончена ли покупка')