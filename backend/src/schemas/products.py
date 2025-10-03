from pydantic import BaseModel, Field, ConfigDict


class ProductCreate(BaseModel):
    """
    Модель для создания или обновления товара
    """
    name: str = Field(min_length=5, max_length=100, description='Название товара')
    description: str | None = Field(default=None, description='Описание товара')
    price: float = Field(description='Цена товара')


class ProductSchema(BaseModel):
    """
    Модель для ответа с данными о товаре
    """
    id: int = Field(description='ID товара')
    name: str = Field(min_length=5, max_length=100, description='Название товара')
    description: str | None = Field(default=None, description='Описание товара')
    price: float = Field(description='Цена товара')
    image_url: str = Field(description='URL изображения товара')
    rating: float = Field(ge=1, le=5, description='Рейтинг товара от 1 до 5')
    seller_id: int = Field(description='ID продавца')

    model_config = ConfigDict(from_attributes=True)