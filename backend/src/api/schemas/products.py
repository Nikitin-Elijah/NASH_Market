from typing import List

from pydantic import BaseModel, Field, ConfigDict

from src.api.schemas.images import ImageSchema


class ProductCreate(BaseModel):
    """
    Модель для создания товара
    """

    name: str = Field(min_length=5, max_length=100, description="Название товара")
    description: str | None = Field(default=None, description="Описание товара")
    price: float = Field(description="Цена товара")


class ProductUpdate(BaseModel):
    """
    Модель для обновления товара
    """

    name: str | None = Field(
        default=None, min_length=5, max_length=100, description="Название товара"
    )
    description: str | None = Field(default=None, description="Описание товара")
    price: float | None = Field(default=None, description="Цена товара")


class ProductSchema(BaseModel):
    """
    Модель для ответа с данными о товаре
    """

    id: int = Field(description="ID товара")
    name: str = Field(min_length=5, max_length=100, description="Название товара")
    description: str | None = Field(default=None, description="Описание товара")
    price: float = Field(description="Цена товара")
    seller_id: int = Field(description="ID продавца")
    is_active: bool = Field(description="Флаг - активен ли товар")
    images: List[ImageSchema] = Field(description="Список изображений")

    model_config = ConfigDict(from_attributes=True)


class PaginatedResponse(BaseModel):
    """
    Модель для ответа пагинации товаров
    """

    items: List[ProductSchema] = Field(description="Список полученных товаров")
    total_count: int = Field(description="Общее количество товаров")
    limit: int = Field(description="Количество товаров на странице")
    next_page_offset: int | None = Field(
        description="Смещение следующей страницы, null если находимся в конце"
    )
