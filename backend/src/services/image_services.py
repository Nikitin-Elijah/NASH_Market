from fastapi import Depends, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import get_current_user
from src.database.db_depends import get_async_db
from src.dependencies.storage import get_s3_client
from src.exceptions.image_exceptions import ImageNotFoundException
from src.models import UserModel, ImageModel
from src.s3_storage.storage import S3Client
from src.utils import generate_product_image_filename, generate_storage_url


class GetImageService:
    def __init__(
        self,
        user: UserModel = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_db),
    ):
        self.user = user
        self.session = session

    async def _get_image(self, image_id: int) -> ImageModel:
        image = await self.session.scalar(
            select(ImageModel).where(ImageModel.id == image_id)
        )
        return image

    @staticmethod
    def _validate(image: ImageModel):
        if not image:
            raise ImageNotFoundException("Image not found")

    async def exec(self, image_id: int) -> ImageModel:
        image = await self._get_image(image_id=image_id)
        self._validate(image=image)
        return image


class AddImageService:
    def __init__(
        self,
        user: UserModel = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_db),
        storage: S3Client = Depends(get_s3_client)
    ):
        self.user = user
        self.session = session
        self.storage = storage

    async def _upload_image_in_s3(
        self, product_id: int, original_filename: str, file_content: bytes
    ) -> str:
        filename = generate_product_image_filename(
            user_id=self.user.id,
            product_id=product_id,
            original_filename=original_filename,
        )
        image_url = generate_storage_url(filename=filename)
        await self.storage.upload_file(
            file_path=None, file_content=file_content, file_name=filename
        )
        return image_url

    async def _add_product_image(
        self, product_id: int, image_url: str, is_main: bool = False
    ) -> ImageModel:
        image = ImageModel(product_id=product_id, url=image_url, is_main=is_main)
        self.session.add(image)
        await self.session.commit()
        await self.session.refresh(image)
        return image

    async def exec(
        self, product_id: int, image: UploadFile, is_main: bool = False
    ) -> ImageModel:
        image_url = await self._upload_image_in_s3(
            product_id=product_id,
            original_filename=image.filename,
            file_content=await image.read(),
        )
        image = await self._add_product_image(
            product_id=product_id, image_url=image_url, is_main=is_main
        )
        return image


class DeleteImageService:
    def __init__(
        self,
        user: UserModel = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_db),
        get_image_service: GetImageService = Depends(),
        storage: S3Client = Depends(get_s3_client)
    ):
        self.user = user
        self.session = session
        self.get_image_service = get_image_service
        self.storage = storage

    async def _delete_image(self, image: ImageModel):
        photo_filename = image.url.split("/")[-1] if image.url else None
        if photo_filename:
            await self.storage.delete_file(object_name=photo_filename)
        await self.session.delete(image)
        await self.session.commit()

    async def exec(self, image_id: int) -> dict:
        image = await self.get_image_service.exec(image_id=image_id)
        await self._delete_image(image=image)
        return {"message": "Image removed successfully"}
