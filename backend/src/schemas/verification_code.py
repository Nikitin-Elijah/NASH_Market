from pydantic import BaseModel, Field, ConfigDict, validator


class VerificationCodeSchema(BaseModel):
    id: int = Field(description='ID попытки регистрации пользователя')
    user_id: int = Field(description='ID пользователя')
    tg_url: str = Field(description='Ссылка на телеграмм бота для регистрации')

    model_config = ConfigDict(from_attributes=True)


class VerifyCodeSchema(BaseModel):
    user_id: int = Field(description='ID пользователя')
    code: int = Field(description='Код для подтверждения регистрации')

    @validator('code')
    def validate_code(cls, v):
        if len(str(v)) != 6:
            raise ValueError('Код должен содержать ровно 6 цифр')

        return v