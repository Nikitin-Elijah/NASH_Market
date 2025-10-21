from pydantic import BaseModel, Field, ConfigDict, EmailStr, validator


class UserCreate(BaseModel):
    """
    Модель для создания и обновления пользователя.
    """
    username: str = Field(max_length=50, description='Имя пользователя')
    password: str = Field(min_length=8, description="Пароль (минимум 8 символов)")
    confirm_password: str = Field(min_length=8, description="Подтвержденный пароль (минимум 8 символов)")

    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Пароли не совпадают')
        return v


class UserSchema(BaseModel):
    """
    Модель для ответа с данными пользователя.
    """
    id: int = Field(description='ID Пользователя')
    username: str = Field(max_length=50, description='Имя пользователя')
    tg_user_id: int = Field(description='Телеграмм ID пользователя')
    tg_username: str = Field(description='Телеграмм username пользователя')
    photo_url: str | None = Field(description='URL ссылка на фото пользователя')

    model_config = ConfigDict(from_attributes=True)