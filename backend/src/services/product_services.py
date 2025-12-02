from dataclasses import dataclass

from fastapi import Depends, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.auth import get_current_user
from src.database.db_depends import get_async_db
from src.exceptions.image_exceptions import ImageNotBelongToProductException
from src.exceptions.product_exceptions import (
    ProductNotFoundException,
    UserIsNotProductOwnerException,
)
from src.models import UserModel, ProductModel, ImageModel
from src.services.image_services import (
    AddImageService,
    GetImageService,
    DeleteImageService,
)


@dataclass
class ProductResponse:
    product: ProductModel
    images: list[ImageModel]


class GetProductService:
    def __init__(self, session: AsyncSession = Depends(get_async_db)):
        self.session = session

    async def _get_product(self, product_id) -> ProductModel:
        product = await self.session.scalar(
            select(ProductModel).where(
                ProductModel.id == product_id, ProductModel.is_active == True
            ).options(selectinload(ProductModel.images))
        )
        return product

    @staticmethod
    def _validate(product: ProductModel):
        if not product:
            raise ProductNotFoundException("Product not found")

    async def exec(self, product_id) -> ProductModel:
        product = await self._get_product(product_id=product_id)
        self._validate(product=product)
        return product


class AddProductService:
    def __init__(
        self,
        user: UserModel = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_db),
        add_image_service: AddImageService = Depends(),
    ):
        self.user = user
        self.session = session
        self.add_image_service = add_image_service

    async def _add_product(
        self, name: str, description: str, price: float
    ) -> ProductModel:
        product = ProductModel(
            name=name, description=description, price=price, seller_id=self.user.id
        )
        self.session.add(product)
        await self.session.commit()
        await self.session.refresh(product)
        return product

    async def exec(
        self, name: str, description: str, price: float, images: list[UploadFile]
    ) -> ProductModel:
        product = await self._add_product(
            name=name, description=description, price=price
        )
        product_images = []
        for pos, image in enumerate(images):
            product_image = await self.add_image_service.exec(
                product_id=product.id, image=image, is_main=True if pos == 0 else False
            )
            product_images.append(product_image)
        await self.session.refresh(product, attribute_names=["images"])
        return product


class AddProductImageService:
    def __init__(
        self,
        user: UserModel = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_db),
        get_product_service: GetProductService = Depends(),
        add_image_service: AddImageService = Depends(),
    ):
        self.user = user
        self.session = session
        self.get_product_service = get_product_service
        self.add_image_service = add_image_service

    def _validate(self, product: ProductModel):
        if product.seller_id != self.user.id:
            raise UserIsNotProductOwnerException(
                "The user is not the owner of the product"
            )

    async def exec(self, product_id: int, images: list[UploadFile]) -> ProductModel:
        product = await self.get_product_service.exec(product_id=product_id)
        self._validate(product=product)
        for image in images:
            await self.add_image_service.exec(
                product_id=product.id,
                image=image,
            )

        await self.session.refresh(product, attribute_names=["images"])
        return product


class UpdateProductService:
    def __init__(
        self,
        user: UserModel = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_db),
        get_product_service: GetProductService = Depends(),
    ):
        self.user = user
        self.session = session
        self.get_product_service = get_product_service

    async def _update_product(self, product: ProductModel, **kwargs) -> ProductModel:
        for key, value in kwargs.items():
            if value is not None:
                setattr(product, key, value)
        await self.session.commit()
        await self.session.refresh(product, ["images"])
        return product

    def _validate(self, product: ProductModel):
        if product.seller_id != self.user.id:
            raise UserIsNotProductOwnerException(
                "The user is not the owner of the product"
            )

    async def exec(self, product_id: int, **kwargs) -> ProductModel:
        product = await self.get_product_service.exec(product_id=product_id)
        self._validate(product=product)
        product = await self._update_product(product=product, **kwargs)
        return product


class SwitchMainImageService:
    def __init__(
        self,
        user: UserModel = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_db),
        get_product_service: GetProductService = Depends(),
        get_image_service: GetImageService = Depends(),
    ):
        self.user = user
        self.session = session
        self.get_product_service = get_product_service
        self.get_image_service = get_image_service

    async def _switch_main_product_image(
        self, product: ProductModel, image_id: int
    ) -> ProductModel:
        await self.session.refresh(product, ["images"])
        for image in product.images:
            image.is_main = True if image.id == image_id else False
        await self.session.commit()
        await self.session.refresh(product, ["images"])
        return product

    def _validate(self, product: ProductModel, image: ImageModel):
        if product.seller_id != self.user.id:
            raise UserIsNotProductOwnerException(
                "The user is not the owner of the product"
            )
        if image.product_id != product.id:
            raise ImageNotBelongToProductException(
                "The image does not belong to this product"
            )

    async def exec(self, product_id: int, image_id: int) -> ProductModel:
        product = await self.get_product_service.exec(product_id=product_id)
        image = await self.get_image_service.exec(image_id=image_id)
        self._validate(product=product, image=image)
        product = await self._switch_main_product_image(
            product=product, image_id=image_id
        )
        return product


class DeleteProductService:
    def __init__(
        self,
        user: UserModel = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_db),
        get_product_service: GetProductService = Depends(),
    ):
        self.user = user
        self.session = session
        self.get_product_service = get_product_service

    async def _delete_product(self, product: ProductModel):
        product.is_active = False
        await self.session.commit()

    def _validate(self, product: ProductModel):
        if product.seller_id != self.user.id:
            raise UserIsNotProductOwnerException(
                "The user is not the owner of the product"
            )

    async def exec(self, product_id: int) -> dict:
        product = await self.get_product_service.exec(product_id=product_id)
        self._validate(product=product)
        await self._delete_product(product=product)
        return {"message": "Product removed successfully"}


class DeleteProductImageService:
    def __init__(
        self,
        user: UserModel = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_db),
        get_product_service: GetProductService = Depends(),
        get_image_service: GetImageService = Depends(),
        delete_image_service: DeleteImageService = Depends(),
    ):
        self.user = user
        self.session = session
        self.get_product_service = get_product_service
        self.get_image_service = get_image_service
        self.delete_image_service = delete_image_service

    def _validate(self, product: ProductModel, image: ImageModel):
        if product.seller_id != self.user.id:
            raise UserIsNotProductOwnerException(
                "The user is not the owner of the product"
            )
        if image.product_id != product.id:
            raise ImageNotBelongToProductException(
                "The image does not belong to this product"
            )

    async def exec(self, product_id: int, image_id: int) -> ProductModel:
        product = await self.get_product_service.exec(product_id=product_id)
        image = await self.get_image_service.exec(image_id=image_id)
        self._validate(product=product, image=image)
        await self.session.refresh(product, ["images"])
        if image.is_main:
            for image in product.images:
                if image.id != image_id:
                    image.is_main = True
                    break
        await self.delete_image_service.exec(image_id=image_id)
        await self.session.refresh(product, ["images"])
        return product
