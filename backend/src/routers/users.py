from typing import List

import jwt
from fastapi import APIRouter, status, UploadFile, HTTPException, Depends, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.auth import verify_password, create_access_token, create_refresh_token, get_current_user
from src.config import SECRET_KEY, ALGORITHM, s3_storage
from src.database.db_depends import get_async_db
from src.models import ProductModel, UserFavoriteModel
from src.models.users import UserModel
from src.schemas.products import ProductSchema
from src.schemas.purchases import PurchaseSchema
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


@router.delete('/{user_id}')
async def delete_user(user_id: int):
    db_user = await UserModel.get(user_id)

    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')

    await db_user.delete()
    return {'detail': 'User successful deleted'}


@router.get('/offers', response_model=List[PurchaseSchema])
async def get_user_offers(
        current_user: UserModel = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_db)
):
    user = await session.scalar(
        select(UserModel)
        .options(selectinload(UserModel.offers))
        .where(UserModel.id == current_user.id)
    )

    return user.offers


@router.get('/purchases', response_model=List[PurchaseSchema])
async def get_user_purchases(
        current_user: UserModel = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_db)
):
    user = await session.scalar(
        select(UserModel)
        .options(selectinload(UserModel.purchases))
        .where(UserModel.id == current_user.id)
    )

    return user.purchases


@router.post('/favorites/{product_id}', status_code=status.HTTP_201_CREATED)
async def add_favorite(product_id: int, current_user: UserModel = Depends(get_current_user)):
    db_product = await ProductModel.get(product_id)

    if not db_product or not db_product.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Product not found')

    db_user_favorites = await UserFavoriteModel.filter(user_id=current_user.id, product_id=product_id)

    if db_user_favorites:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='The user has already added the product to their favorites'
        )

    favorite = await UserFavoriteModel.create(
        user_id=current_user.id,
        product_id=product_id
    )

    return {"status": "added", "favorite_id": favorite.id}


@router.get('/favorites', response_model=List[ProductSchema])
async def get_favorite_products(
        current_user: UserModel = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_db)
):
    stmt = (select(ProductModel)
            .join(UserFavoriteModel, ProductModel.id == UserFavoriteModel.product_id)
            .where(UserFavoriteModel.user_id == current_user.id)
            .options(selectinload(ProductModel.images)))

    result = (await session.scalars(stmt)).all()
    return result


@router.delete('/favorites/{product_id}')
async def delete_favorite(product_id: int, current_user: UserModel = Depends(get_current_user)):
    db_user_favorites = await UserFavoriteModel.filter(product_id=product_id, user_id=current_user.id)

    if not db_user_favorites:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Favorite not found')

    db_user_favorite = db_user_favorites[0]
    await db_user_favorite.delete()

    return {"status": "removed"}