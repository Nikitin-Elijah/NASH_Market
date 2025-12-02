import jwt
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import (
    verify_password,
    create_access_token,
    create_refresh_token,
    get_current_user,
)
from src.config import SECRET_KEY, ALGORITHM
from src.database.db_depends import get_async_db
from src.dependencies.storage import get_s3_client
from src.exceptions.user_exceptions import (
    UserAuthServiceException,
    UserRefreshServiceException,
    UserNotFoundException,
)
from src.exceptions.user_favorite_exceptions import UserFavoriteNotFoundException
from src.models import UserModel, UserFavoriteModel
from src.s3_storage.storage import S3Client
from src.services.product_services import GetProductService
from src.utils import generate_avatar_filename, generate_storage_url


class GetUserService:
    def __init__(self, session: AsyncSession = Depends(get_async_db)):
        self.session = session

    async def _get_user(self, user_id: int) -> UserModel | None:
        user = await self.session.scalar(
            select(UserModel).where(
                UserModel.id == user_id, UserModel.is_active == True
            )
        )
        return user

    @staticmethod
    def _validate(user: UserModel | None):
        if not user:
            raise UserNotFoundException("User Not Found")

    async def exec(self, user_id: int) -> UserModel:
        user = await self._get_user(user_id=user_id)
        self._validate(user=user)
        return user


class GetNotActiveUserService:
    def __init__(self, session: AsyncSession = Depends(get_async_db)):
        self.session = session

    async def _get_user(self, user_id: int) -> UserModel | None:
        user = await self.session.scalar(
            select(UserModel).where(UserModel.id == user_id)
        )
        return user

    @staticmethod
    def _validate(user: UserModel | None):
        if not user:
            raise UserNotFoundException("User Not Found")

    async def exec(self, user_id: int) -> UserModel:
        user = await self._get_user(user_id=user_id)
        self._validate(user=user)
        return user


class GetUserByNameService:
    def __init__(self, session: AsyncSession = Depends(get_async_db)):
        self.session = session

    async def _get_user_by_name(self, username: str) -> UserModel | None:
        result = await self.session.scalar(
            select(UserModel).where(UserModel.username == username)
        )
        return result

    async def exec(self, username: str) -> UserModel:
        user = await self._get_user_by_name(username=username)
        return user


class GetUserByTGIDService:
    def __init__(self, session: AsyncSession = Depends(get_async_db)):
        self.session = session

    async def _get_user_by_tg_id(self, tg_user_id: int) -> UserModel | None:
        result = await self.session.scalar(
            select(UserModel).where(UserModel.tg_user_id == tg_user_id)
        )
        return result

    async def exec(self, tg_user_id: int) -> UserModel:
        user = await self._get_user_by_tg_id(tg_user_id=tg_user_id)
        return user


class UserAuthService:
    def __init__(
        self,
        session: AsyncSession = Depends(get_async_db),
        get_user_by_name: GetUserByNameService = Depends(),
    ):
        self.session = session
        self.get_user_by_name = get_user_by_name

    @staticmethod
    def _validate(user: UserModel | None, password: str):
        if not user or not verify_password(password, user.hashed_password):
            raise UserAuthServiceException("Incorrect username or password")

    async def exec(self, username: str, password: str) -> dict:
        user = await self.get_user_by_name.exec(username=username)
        self._validate(user=user, password=password)
        access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username}
        )
        refresh_token = create_refresh_token(
            data={"sub": str(user.id), "username": user.username}
        )
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }


class UserRefreshService:
    def __init__(
        self,
        session: AsyncSession = Depends(get_async_db),
        get_user_by_name: GetUserByNameService = Depends(),
    ):
        self.session = session
        self.get_user_by_name = get_user_by_name

    @staticmethod
    def _validate_token(refresh_token: str) -> str:
        try:
            payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("username")
            if username is None:
                raise UserRefreshServiceException("Could not validate refresh token")
        except jwt.exceptions:
            raise UserRefreshServiceException("Could not validate refresh token")
        return username

    @staticmethod
    def _validate_user(user: UserModel | None):
        if user is None:
            raise UserRefreshServiceException("Could not validate refresh token")

    async def exec(self, refresh_token: str) -> dict:
        username = self._validate_token(refresh_token=refresh_token)
        user = await self.get_user_by_name.exec(username=username)
        self._validate_user(user=user)
        access_token = create_access_token(
            data={"sub": user.tg_user_id, "username": user.username, "id": user.id}
        )
        return {"access_token": access_token, "token_type": "bearer"}


class UploadUserPhotoService:
    def __init__(
        self,
        user: UserModel = Depends(get_current_user),
        storage: S3Client = Depends(get_s3_client),
    ):
        self.user = user
        self.storage = storage

    async def _upload_image(self, original_filename: str, file_content: bytes) -> str:
        filename = generate_avatar_filename(
            original_filename=original_filename, user_id=self.user.id
        )
        photo_url = generate_storage_url(filename=filename)
        await self.storage.upload_file(
            file_path=None, file_content=file_content, file_name=filename
        )
        return photo_url

    async def _update_user_photo(self, photo_url: str):
        self.user.photo_url = photo_url
        await self.user.save()

    async def exec(self, original_filename: str, file_content: bytes) -> UserModel:
        photo_url = await self._upload_image(
            original_filename=original_filename, file_content=file_content
        )
        await self._update_user_photo(photo_url=photo_url)
        return self.user


class GetUserFavoriteService:
    def __init__(
        self,
        user: UserModel = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_db),
    ):
        self.user = user
        self.session = session

    async def _get_user_favorite(
        self, user_id: int, product_id: int
    ) -> UserFavoriteModel | None:
        user_favorite = await self.session.scalar(
            select(UserFavoriteModel).where(
                UserFavoriteModel.user_id == user_id,
                UserFavoriteModel.product_id == product_id,
            )
        )
        return user_favorite

    async def exec(self, user_id: int, product_id: int) -> UserFavoriteModel:
        return await self._get_user_favorite(user_id=user_id, product_id=product_id)


class AddUserFavoriteService:
    def __init__(
        self,
        user: UserModel = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_db),
        get_product_service: GetProductService = Depends(),
        get_user_favorite_service: GetUserFavoriteService = Depends(),
    ):
        self.user = user
        self.session = session
        self.get_product_service = get_product_service
        self.get_user_favorite_service = get_user_favorite_service

    async def _add_user_favorite(
        self, user_id: int, product_id: int
    ) -> UserFavoriteModel:
        user_favorite = UserFavoriteModel(user_id=user_id, product_id=product_id)
        self.session.add(user_favorite)
        await self.session.commit()
        await self.session.refresh(user_favorite)
        return user_favorite

    async def exec(self, product_id: int):
        await self.get_product_service.exec(product_id=product_id)
        user_favorite = await self.get_user_favorite_service.exec(
            user_id=self.user.id, product_id=product_id
        )
        if user_favorite:
            return {"status": "already_exists", "favorite_id": user_favorite.id}
        user_favorite = await self._add_user_favorite(
            user_id=self.user.id, product_id=product_id
        )
        return {"status": "added", "favorite_id": user_favorite.id}


class DeleteUserFavoriteService:
    def __init__(
        self,
        user: UserModel = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_db),
    ):
        self.user = user
        self.session = session

    async def _get_user_favorite(
        self, user_id: int, product_id: int
    ) -> UserFavoriteModel | None:
        user_favorite = await self.session.scalar(
            select(UserFavoriteModel).where(
                UserFavoriteModel.user_id == user_id,
                UserFavoriteModel.product_id == product_id,
            )
        )
        return user_favorite

    async def _delete_user_favorite(self, user_favorite: UserFavoriteModel):
        await self.session.delete(user_favorite)
        await self.session.commit()

    @staticmethod
    def _validate(user_favorite: UserFavoriteModel):
        if not user_favorite:
            raise UserFavoriteNotFoundException("Favorite not found")

    async def exec(self, product_id: int) -> dict:
        user_favorite = await self._get_user_favorite(
            user_id=self.user.id, product_id=product_id
        )
        self._validate(user_favorite=user_favorite)
        await self._delete_user_favorite(user_favorite=user_favorite)
        return {"status": "removed"}


class RecalculateUserRatingService:
    def __init__(
        self,
        session: AsyncSession = Depends(get_async_db),
        get_user_service: GetUserService = Depends(),
    ):
        self.session = session
        self.get_user_service = get_user_service

    async def _recalculate_user_rating(self, user: UserModel):
        await self.session.refresh(user, ["received_reviews"])
        update_seller_rating = sum([r.rating for r in user.received_reviews]) / len(
            user.received_reviews
        )
        user.rating = update_seller_rating
        await self.session.commit()

    async def exec(self, user_id: int):
        user = await self.get_user_service.exec(user_id=user_id)
        await self._recalculate_user_rating(user=user)
