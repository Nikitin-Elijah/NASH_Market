from typing import List

from fastapi import APIRouter, status, UploadFile, Depends, File
from fastapi.security import OAuth2PasswordRequestForm

from src.api.api_services.user_api_services import (
    UserAuthAPIService,
    UploadUserPhotoAPIService,
    GetUserOffersAPIService,
    GetUserPurchasesAPIService,
    UserRefreshAPIService,
    AddUserFavoriteAPIService,
    GerUserFavoritesAPIService,
    DeleteUserFavoriteAPIService,
    GetUserAPIService,
    GetUserByTGIDAPIService,
)
from src.auth import get_current_user
from src.models.users import UserModel
from src.api.schemas.products import ProductSchema
from src.api.schemas.purchases import PurchaseSchema
from src.api.schemas.users import UserSchema


router = APIRouter(prefix="/users", tags=["users"])


@router.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_auth_api_service: UserAuthAPIService = Depends(),
):
    """
    Аутентифицирует пользователя и возвращает access_token и refresh_token.
    """
    return await user_auth_api_service.exec(form_data.username, form_data.password)


@router.post("/refresh-token")
async def refresh_token(
    refresh_token: str,
    user_refresh_api_service: UserRefreshAPIService = Depends(),
):
    """
    Обновляет access_token с помощью refresh_token.
    """
    return await user_refresh_api_service.exec(refresh_token=refresh_token)


@router.get("/me", response_model=UserSchema)
async def get_me(current_user: UserModel = Depends(get_current_user)):
    """
    Возвращает информацию о текущем пользователе
    """
    return current_user


@router.get("/me/offers", response_model=List[PurchaseSchema])
async def get_user_offers(
    get_user_offers_api_service: GetUserOffersAPIService = Depends(),
):
    """
    Возвращает список предложений о покупке пользователю
    """
    return await get_user_offers_api_service.exec()


@router.get("/me/purchases", response_model=List[PurchaseSchema])
async def get_user_purchases(
    get_user_purchases_api_service: GetUserPurchasesAPIService = Depends(),
):
    """
    Возвращает список покупок пользователя
    """
    return await get_user_purchases_api_service.exec()


@router.get("/me/favorites", response_model=List[ProductSchema])
async def get_favorite_products(
    get_user_favorites_api_service: GerUserFavoritesAPIService = Depends(),
):
    """
    Возвращает избранные товары пользователя
    """
    return await get_user_favorites_api_service.exec()


@router.patch("/me/upload-photo", response_model=UserSchema)
async def upload_photo(
    photo: UploadFile = File(...),
    upload_user_photo_api_service: UploadUserPhotoAPIService = Depends(),
):
    """
    Обновляет фото пользователя
    """
    return await upload_user_photo_api_service.exec(
        file_content=await photo.read(), original_filename=photo.filename
    )


@router.delete("/me/favorites/{product_id}")
async def delete_favorite(
    product_id: int,
    delete_user_favorite_api_service: DeleteUserFavoriteAPIService = Depends(),
):
    """
    Удаляет товар из избранного пользователя
    """
    return await delete_user_favorite_api_service.exec(product_id=product_id)



@router.post("/me/favorites/{product_id}", status_code=status.HTTP_201_CREATED)
async def add_favorite(
    product_id: int,
    add_user_favorite_api_service: AddUserFavoriteAPIService = Depends(),
):
    """
    Добавляет товар по его id в избранные пользователя
    """
    return await add_user_favorite_api_service.exec(product_id=product_id)


@router.get("/{user_id}", response_model=UserSchema)
async def get_user(user_id: int, get_user_api_service: GetUserAPIService = Depends()):
    return await get_user_api_service.exec(user_id=user_id)


@router.get("/tg/{tg_user_id}")
async def get_user_by_tg_user_id(
    tg_user_id: int,
    get_user_by_tg_user_id_api_service: GetUserByTGIDAPIService = Depends(),
):
    return await get_user_by_tg_user_id_api_service.exec(tg_user_id=tg_user_id)
