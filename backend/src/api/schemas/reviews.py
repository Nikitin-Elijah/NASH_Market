from pydantic import BaseModel, Field, ConfigDict


class ReviewCreate(BaseModel):
    """
    Модель для создания отзыва
    """

    purchase_id: int = Field(description="ID записи о покупке")
    rating: int = Field(ge=1, le=5, description="Оценка от 1 до 5")
    text: str = Field(min_length=5, max_length=100, description="Текст отзыва")


class ReviewSchema(BaseModel):
    """
    Модель для ответа с данными об отзыве
    """

    id: int = Field(description="ID Отзыва")
    author_id: int = Field(description="ID Автора")
    recipient_id: int = Field(description="ID Получателя")
    purchase_id: int = Field(description="ID записи о покупке")
    rating: int = Field(ge=1, le=5, description="Оценка от 1 до 5")
    text: str = Field(min_length=5, max_length=100, description="Текст отзыва")

    model_config = ConfigDict(from_attributes=True)
