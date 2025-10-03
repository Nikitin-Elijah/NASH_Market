from pydantic import BaseModel, Field, ConfigDict, EmailStr


class UserCreate(BaseModel):
    """
    Модель для создания и обновления пользователя.
    """
    username: str = Field(max_length=50, description='Имя пользователя')
    email: EmailStr = Field(description='Еmail пользователя')
    password: str = Field(min_length=8, description="Пароль (минимум 8 символов)")


class UserSchema(BaseModel):
    """
    Модель для ответа с данными пользователя.
    """
    id: int = Field(description='ID Пользователя')
    username: str = Field(max_length=50, description='Имя пользователя')
    email: EmailStr = Field(description='Еmail пользователя')
    photo_url: str | None = Field(description='URL ссылка на фото пользователя')

    model_config = ConfigDict(from_attributes=True)