from pydantic import BaseModel, Field, ConfigDict


class ImageSchema(BaseModel):
    """
    Модель для ответа с данными об изображении
    """
    id: int = Field(description='ID Изображения')
    product_id: int = Field(description='ID Товара')
    url: str = Field(description='URL Изображения')
    is_main: bool = Field(description='Флаг - главное изображение')

    model_config = ConfigDict(from_attributes=True)