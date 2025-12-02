from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.exceptions.product_exceptions import ProductNotFoundException
from src.exceptions.user_exceptions import (
    UserAuthServiceException,
    UserRefreshServiceException, UserNotFoundException,
)
from src.exceptions.user_favorite_exceptions import UserFavoriteNotFoundException
from src.models import UserModel, PurchaseModel, ProductModel, UserFavoriteModel
from src.auth import get_current_user
from src.database.db_depends import get_async_db
from src.services.user_services import (
    UserAuthService,
    UploadUserPhotoService,
    UserRefreshService,
    AddUserFavoriteService,
    DeleteUserFavoriteService, GetUserService, GetUserByTGIDService,
)


class UserAuthAPIService:
    """
    API Сервис для аутентификации пользователя
    """

    def __init__(
        self,
        session: AsyncSession = Depends(get_async_db),
        user_auth_service: UserAuthService = Depends(),
    ):
        self.session = session
        self.user_auth_service = user_auth_service

    async def exec(self, username: str, password: str):
        try:
            return await self.user_auth_service.exec(
                username=username, password=password
            )
        except UserAuthServiceException as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e),
                headers={"WWW-Authenticate": "Bearer"},
            )


class UserRefreshAPIService:
    """
    API Сервис для обновления access токена
    """

    def __init__(
        self, user_refresh_service: UserRefreshService = Depends()
    ):
        self.user_refresh_service = user_refresh_service

    async def exec(self, refresh_token: str) -> dict:
        try:
            return await self.user_refresh_service.exec(refresh_token=refresh_token)
        except UserRefreshServiceException as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e),
                headers={"WWW-Authenticate": "Bearer"},
            )


class GetUserAPIService:
    """
    API Сервис для получения пользователя по id
    """
    def __init__(self, get_user_service: GetUserService = Depends()):
        self.get_user_service = get_user_service

    async def exec(self, user_id: int) -> UserModel:
        try:
            return await self.get_user_service.exec(user_id=user_id)
        except UserNotFoundException as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


class GetUserByTGIDAPIService:
    """
    API Сервис для получения пользователя по его telegram id
    """
    def __init__(self, get_user_by_tg_id_service: GetUserByTGIDService = Depends()):
        self.get_user_by_tg_id_service = get_user_by_tg_id_service

    async def exec(self, tg_user_id: int) -> UserModel | None:
        return await self.get_user_by_tg_id_service.exec(tg_user_id=tg_user_id)


class UploadUserPhotoAPIService:
    """
    API Сервис для обновления фото пользователя
    """

    def __init__(
        self,
        user: UserModel = Depends(get_current_user),
        upload_user_photo_service: UploadUserPhotoService = Depends(

        ),
    ):
        self.user = user
        self.upload_user_photo_service = upload_user_photo_service

    async def exec(self, original_filename: str, file_content: bytes) -> UserModel:
        return await self.upload_user_photo_service.exec(
            original_filename, file_content
        )


class GetUserOffersAPIService:
    """
    API Сервис для получения всех предложений пользователю о покупке
    """

    def __init__(
        self,
        user: UserModel = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_db),
    ):
        self.user = user
        self.session = session

    async def exec(self) -> list[PurchaseModel]:
        await self.session.refresh(self.user, attribute_names=["offers"])
        return self.user.offers


class GetUserPurchasesAPIService:
    """
    API Сервис для получения всех предложений о покупке пользователя
    """

    def __init__(
        self,
        user: UserModel = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_db),
    ):
        self.user = user
        self.session = session

    async def exec(self) -> list[PurchaseModel]:
        await self.session.refresh(self.user, attribute_names=["purchases"])
        return self.user.purchases


class AddUserFavoriteAPIService:
    """
    API сервис для добавления товара в избранное пользователя
    """

    def __init__(
        self,
        add_user_favorite_service: AddUserFavoriteService = Depends(

        ),
    ):
        self.add_user_favorite_service = add_user_favorite_service

    async def exec(self, product_id: int) -> dict:
        try:
            return await self.add_user_favorite_service.exec(product_id=product_id)
        except ProductNotFoundException as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


class GerUserFavoritesAPIService:
    """
    API Сервис для получения избранных товаров пользователя
    """

    def __init__(
        self,
        user: UserModel = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_db),
    ):
        self.user = user
        self.session = session

    async def exec(self):
        stmt = (
            select(ProductModel)
            .join(UserFavoriteModel, ProductModel.id == UserFavoriteModel.product_id)
            .where(UserFavoriteModel.user_id == self.user.id)
            .options(selectinload(ProductModel.images))
        )

        favorites = (await self.session.scalars(stmt)).all()
        return favorites


class DeleteUserFavoriteAPIService:
    """
    API Сервис для удаления товара из избранного пользователя
    """

    def __init__(
        self,
        delete_user_favorite_service: DeleteUserFavoriteService = Depends(

        ),
    ):
        self.delete_user_favorite_service = delete_user_favorite_service

    async def exec(self, product_id: int) -> dict:
        try:
            return await self.delete_user_favorite_service.exec(product_id=product_id)
        except UserFavoriteNotFoundException as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
