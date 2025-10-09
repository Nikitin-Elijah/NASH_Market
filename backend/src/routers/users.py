from typing import List

import jwt
from fastapi import APIRouter, status, UploadFile, HTTPException, Depends, Form
from fastapi.security import OAuth2PasswordRequestForm

from src.auth import verify_password, create_access_token, create_refresh_token, get_current_user
from src.config import SECRET_KEY, ALGORITHM, s3_storage
from src.models.users import UserModel
from src.schemas.users import UserSchema
from src.utils import generate_avatar_filename, generate_storage_url

router = APIRouter(prefix='/users', tags=['users'])


@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Аутентифицирует пользователя и возвращает access_token и refresh_token.
    """
    result = await UserModel.filter(username=form_data.username)
    user = result[0] if result else None

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": str(user.tg_user_id), "username": user.username, "id": user.id})
    refresh_token = create_refresh_token(data={"sub": str(user.tg_user_id), "username": user.username, "id": user.id})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/refresh-token")
async def refresh_token(refresh_token: str):
    """
    Обновляет access_token с помощью refresh_token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("username")

        if username is None:
            raise credentials_exception

    except jwt.exceptions:
        raise credentials_exception

    result = await UserModel.filter(username=username)
    user = result[0] if result else None

    if user is None:
        raise credentials_exception

    access_token = create_access_token(data={"sub": user.tg_user_id, "username": user.username, "id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get('/', response_model=List[UserSchema])
async def get_all_users(current_user: UserModel = Depends(get_current_user)):
    return await UserModel.filter(is_active=True)


@router.get('/me', response_model=UserSchema)
async def get_me(current_user: UserModel = Depends(get_current_user)):
    return current_user


@router.put('/upload-photo', response_model=UserSchema)
async def upload_photo(
    current_user: UserModel = Depends(get_current_user),
    photo: UploadFile = Form(...)
):
    file_content = await photo.read()
    original_filename = photo.filename
    db_user = await UserModel.get(current_user.id)
    old_photo_filename = db_user.photo_url.split('/')[-1] if db_user.photo_url else None
    filename = generate_avatar_filename(original_filename=original_filename, user_id=db_user.id)
    photo_url = generate_storage_url(filename=filename)

    await s3_storage.upload_file(
        file_path=None,
        file_content=file_content,
        file_name=filename
    )

    db_user.photo_url = photo_url
    await db_user.save()

    if old_photo_filename:
        await s3_storage.delete_file(object_name=old_photo_filename)

    return db_user
