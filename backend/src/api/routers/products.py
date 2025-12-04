from typing import List

from fastapi import APIRouter, status, UploadFile, Depends, Query, File

from src.api.api_services.product_api_services import (
    AddProductAPIService,
    AddProductImageAPIService,
    GetUserProductsAPIService,
    GetProductAPIService,
    UpdateProductAPIService,
    SwitchMainImageAPIService,
    DeleteProductAPIService,
    DeleteProductImageAPIService,
    SearchProductsAPIService,
    PaginatedProductsAPIService,
)
from src.config import ES
from src.api.schemas.products import (
    ProductSchema,
    ProductCreate,
    PaginatedResponse,
    ProductUpdate,
)
from src.search_service.es_update_products_service import ESUpdateProductsService

router = APIRouter(prefix="/products", tags=["products"])


@router.post("", response_model=ProductSchema, status_code=status.HTTP_201_CREATED)
async def create_product(
    request_schema: ProductCreate = Depends(),
    images: List[UploadFile] = File(None),
    add_product_api_srvice: AddProductAPIService = Depends(),
):
    """
    Создает Товар
    """
    return await add_product_api_srvice.exec(
        **request_schema.model_dump(), images=images
    )


@router.post(
    "/{product_id}/images",
    response_model=ProductSchema,
    status_code=status.HTTP_201_CREATED,
)
async def add_product_images(
    product_id: int,
    images: List[UploadFile] = File(None),
    add_product_image_api_service: AddProductImageAPIService = Depends(),
):
    """
    Добавляет изображения для товара
    """
    return await add_product_image_api_service.exec(
        product_id=product_id, images=images
    )


@router.get("/user/{user_id}", response_model=PaginatedResponse)
async def get_user_products(
    user_id: int,
    limit: int = Query(10, ge=1, le=100, description="Размер страницы"),
    offset: int = Query(0, ge=0, description="Смещение следующей страницы"),
    get_user_products_api_service: GetUserProductsAPIService = Depends(),
):
    """
    Возвращает товары пользователя
    """
    return await get_user_products_api_service.exec(
        user_id=user_id, limit=limit, offset=offset
    )


@router.get("/{product_id}", response_model=ProductSchema)
async def get_product_per_id(
    product_id: int,
    get_product_api_service: GetProductAPIService = Depends(),
):
    """
    Возвращает товар по его id
    """
    return await get_product_api_service.exec(product_id=product_id)


@router.get("", response_model=PaginatedResponse)
async def paginated_products(
    limit: int = Query(10, ge=1, le=100, description="Размер страницы"),
    offset: int = Query(0, ge=0, description="Смещение следующей страницы"),
    saved_total_count: int | None = Query(None),
    paginated_products_api_service: PaginatedProductsAPIService = Depends(),
):
    """
    Пагинация товаров
    """
    return await paginated_products_api_service.exec(limit=limit, offset=offset, saved_total_count=saved_total_count)


@router.get("/update-es")
async def update_es():
    updater = ESUpdateProductsService(es=ES)
    await updater.update_products()
    return {"message": "OK"}


@router.put("/{product_id}", response_model=ProductSchema)
async def update_product(
    product_id: int,
    request_schema: ProductUpdate = Depends(),
    update_product_api_service: UpdateProductAPIService = Depends(),
):
    """
    Обновление товара по его id
    """
    return await update_product_api_service.exec(
        product_id=product_id, **request_schema.model_dump(exclude_unset=True)
    )


@router.patch("/{product_id}/images/{image_id}/main", response_model=ProductSchema)
async def set_main_product_image(
    product_id: int,
    image_id: int,
    switch_main_image_api_service: SwitchMainImageAPIService = Depends(),
):
    """
    Изменение главного изображения товара
    """
    return await switch_main_image_api_service.exec(
        product_id=product_id, image_id=image_id
    )


@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    delete_product_api_service: DeleteProductAPIService = Depends(),
):
    """
    Удаление товара по его id
    """
    return await delete_product_api_service.exec(product_id=product_id)


@router.delete("/{product_id}/images/{image_id}", response_model=ProductSchema)
async def delete_product_image(
    product_id: int,
    image_id: int,
    delete_product_image_api_service: DeleteProductImageAPIService = Depends(),
):
    """
    Удаление изображение товара
    """
    return await delete_product_image_api_service.exec(
        product_id=product_id, image_id=image_id
    )


@router.get("/search", response_model=PaginatedResponse)
async def search_product_by_query(
    query: str,
    limit: int = Query(10, ge=1, le=100, description="Размер страницы"),
    offset: int = Query(0, ge=0, description="Смещение следующей страницы"),
    search_products_api_service: SearchProductsAPIService = Depends(),
):
    """
    Поиск товаров
    """
    return await search_products_api_service.exec(
        query=query, limit=limit, offset=offset
    )
