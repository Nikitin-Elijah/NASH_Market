from fastapi import Depends, UploadFile, HTTPException, status
from sqlalchemy import select, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.api.schemas.products import PaginatedResponse
from src.cache.cache import redis_cache, cache_delete_prefix
from src.config import PRODUCTS_SEARCHER
from src.database.db_depends import get_async_db
from src.exceptions.image_exceptions import (
    ImageNotFoundException,
    ImageNotBelongToProductException,
)
from src.exceptions.product_exceptions import (
    ProductNotFoundException,
    UserIsNotProductOwnerException,
)
from src.models import ProductModel
from src.services.product_services import (
    AddProductService,
    AddProductImageService,
    GetProductService,
    UpdateProductService,
    SwitchMainImageService,
    DeleteProductService,
    DeleteProductImageService,
)


class AddProductAPIService:
    """
    API Сервис для добавления товара
    """

    def __init__(self, add_product_service: AddProductService = Depends()):
        self.add_product_service = add_product_service

    async def exec(
        self, name: str, description: str, price: float, images: list[UploadFile]
    ) -> ProductModel:
        product = await self.add_product_service.exec(name, description, price, images)
        await cache_delete_prefix(prefix="products")
        return product


class AddProductImageAPIService:
    """
    API Сервис для добавления нового изображения для товара
    """

    def __init__(
        self,
        add_product_image_service: AddProductImageService = Depends(),
    ):
        self.add_product_image_service = add_product_image_service

    async def exec(self, product_id: int, images: list[UploadFile]) -> ProductModel:
        try:
            await cache_delete_prefix(prefix="products")
            return await self.add_product_image_service.exec(
                product_id=product_id, images=images
            )
        except ProductNotFoundException as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except UserIsNotProductOwnerException as e:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


class GetUserProductsAPIService:
    """
    API Сервис для получения всех товаров пользователя
    """

    def __init__(
        self,
        session: AsyncSession = Depends(get_async_db),
    ):
        self.session = session

    async def _get_user_products(
        self, user_id: int, limit: int, offset: int
    ) -> PaginatedResponse:
        products = (
            await self.session.scalars(
                select(ProductModel)
                .where(
                    ProductModel.seller_id == user_id, ProductModel.is_active == True
                )
                .order_by(ProductModel.id.desc())
                .options(selectinload(ProductModel.images))
            )
        ).all()

        if not products:
            return PaginatedResponse(
                items=[], total_count=0, limit=limit, next_page_offset=None
            )
        total_count = len(products)
        items = (
            products[offset : offset + limit]
            if offset + limit < total_count
            else products[offset:]
        )
        next_page_offset = offset + limit if offset + limit < total_count else None
        return PaginatedResponse(
            items=items,
            total_count=total_count,
            limit=limit,
            next_page_offset=next_page_offset,
        )

    @redis_cache(prefix="products", ttl=1200)
    async def exec(self, user_id: int, limit: int, offset: int) -> PaginatedResponse:
        return await self._get_user_products(
            user_id=user_id, limit=limit, offset=offset
        )


class GetProductAPIService:
    """
    API Сервис для получения товара по его id
    """

    def __init__(self, get_product_service: GetProductService = Depends()):
        self.get_product_service = get_product_service

    @redis_cache(prefix="products", ttl=1200)
    async def exec(self, product_id) -> ProductModel:
        try:
            return await self.get_product_service.exec(product_id=product_id)
        except ProductNotFoundException as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


class UpdateProductAPIService:
    """
    API Сервис для обновления товара
    """

    def __init__(
        self,
        update_product_service: UpdateProductService = Depends(),
    ):
        self.update_product_service = update_product_service

    async def exec(self, product_id: int, **kwargs) -> ProductModel:
        try:
            await cache_delete_prefix(prefix="products")
            return await self.update_product_service.exec(
                product_id=product_id, **kwargs
            )
        except ProductNotFoundException as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except UserIsNotProductOwnerException as e:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


class SwitchMainImageAPIService:
    """
    API Сервис для смены главного изображения для товара
    """

    def __init__(
        self,
        switch_main_image_service: SwitchMainImageService = Depends(),
    ):
        self.switch_main_image_service = switch_main_image_service

    async def exec(self, product_id: int, image_id: int) -> ProductModel:
        try:
            await cache_delete_prefix(prefix="products")
            return await self.switch_main_image_service.exec(
                product_id=product_id, image_id=image_id
            )
        except ProductNotFoundException as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except UserIsNotProductOwnerException as e:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
        except ImageNotFoundException as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except ImageNotBelongToProductException as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


class DeleteProductAPIService:
    """
    API Сервис для удаления товара
    """

    def __init__(
        self,
        delete_product_service: DeleteProductService = Depends(),
    ):
        self.delete_product_service = delete_product_service

    async def exec(self, product_id: int) -> dict:
        try:
            await cache_delete_prefix(prefix="products")
            return await self.delete_product_service.exec(product_id=product_id)
        except ProductNotFoundException as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except UserIsNotProductOwnerException as e:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


class DeleteProductImageAPIService:
    """
    API Сервис для удаления изображения товара
    """

    def __init__(
        self,
        delete_product_image_service: DeleteProductImageService = Depends(),
    ):
        self.delete_product_image_service = delete_product_image_service

    async def exec(self, product_id: int, image_id: int) -> ProductModel:
        try:
            await cache_delete_prefix(prefix="products")
            return await self.delete_product_image_service.exec(
                product_id=product_id, image_id=image_id
            )
        except ProductNotFoundException as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except ImageNotFoundException as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except UserIsNotProductOwnerException as e:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
        except ImageNotBelongToProductException as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


class SearchProductsAPIService:
    """
    API Сервис для поиска товаров
    """

    def __init__(self, session: AsyncSession = Depends(get_async_db)):
        self.session = session

    async def _search_products(self, query: str, limit: int, offset: int):
        response = PRODUCTS_SEARCHER.search_cards(
            query=query, count=limit, offset=offset
        )
        ids = list(map(int, response.card_ids))
        if not ids:
            return PaginatedResponse(
                items=[],
                total_count=response.total_count,
                limit=limit,
                next_page_offset=response.next_card_offset,
            )
        order = case(
            {id_: index for index, id_ in enumerate(ids)}, value=ProductModel.id
        )
        stmt = (
            select(ProductModel)
            .where(ProductModel.id.in_(ids))
            .options(selectinload(ProductModel.images))
            .order_by(order)
        )
        products = (await self.session.scalars(stmt)).all()
        return PaginatedResponse(
            items=products,
            total_count=response.total_count,
            limit=limit,
            next_page_offset=response.next_card_offset,
        )

    @redis_cache(prefix="products", ttl=1200)
    async def exec(self, query: str, limit: int, offset: int) -> PaginatedResponse:
        return await self._search_products(query=query, limit=limit, offset=offset)


class GetAllProductsAPIService:
    """
    API Сервис для получения продуктов
    """

    def __init__(self, session: AsyncSession = Depends(get_async_db)):
        self.session = session

    async def _get_all_products(self) -> list[int]:
        products_ids = (
            await self.session.scalars(
                select(ProductModel.id)
                .where(ProductModel.is_active == True)
                .order_by(ProductModel.id.desc())
            )
        ).all()
        return products_ids

    @redis_cache(prefix="products", ttl=60)
    async def exec(self) -> list[int]:
        return await self._get_all_products()


class PaginatedProductsAPIService:
    """
    API Сервис для пагинации всех товаров
    """

    def __init__(self, session: AsyncSession = Depends(get_async_db)):
        self.session = session

    async def _paginated_products(
        self, limit: int, offset: int, saved_total_count: int | None
    ) -> PaginatedResponse:
        db_products = (
            await self.session.scalars(
                select(ProductModel)
                .where(ProductModel.is_active == True)
                .order_by(ProductModel.id.desc())
                .options(selectinload(ProductModel.images))
            )
        ).all()
        if not db_products:
            return PaginatedResponse(
                items=[], total_count=0, limit=limit, next_page_offset=None
            )
        total_count = len(db_products)
        add_offset = 0
        if saved_total_count and total_count > saved_total_count:
            add_offset = total_count - saved_total_count
        items = (
            db_products[offset + add_offset : offset + add_offset + limit]
            if offset + add_offset + limit < total_count
            else db_products[offset + add_offset :]
        )
        next_page_offset = (
            offset + limit + add_offset
            if offset + limit + add_offset < total_count
            else None
        )
        return PaginatedResponse(
            items=items,
            total_count=total_count,
            limit=limit,
            next_page_offset=next_page_offset,
        )

    @redis_cache(prefix="products", ttl=1200)
    async def exec(
        self, limit: int, offset: int, saved_total_count: int | None
    ) -> PaginatedResponse:
        return await self._paginated_products(
            limit=limit, offset=offset, saved_total_count=saved_total_count
        )
