from typing import List, Optional

from fastapi import APIRouter, status, Form, UploadFile, Depends, HTTPException, Query, File
from sqlalchemy import select, update, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.auth import get_current_user
from src.config import s3_storage, PRODUCTS_SEARCHER, ES
from src.database.db_depends import get_async_db
from src.models import UserModel, ProductModel, ImageModel
from src.schemas.products import ProductSchema, ProductCreate, PaginatedResponse
from src.search_service.es_update_products_service import ESUpdateProductsService
from src.utils import generate_product_image_filename, generate_storage_url

router = APIRouter(prefix='/products', tags=['products'])


@router.post('/', response_model=ProductSchema, status_code=status.HTTP_201_CREATED)
async def create_product(
        request_schema: ProductCreate = Depends(ProductCreate),
        images: List[UploadFile] = File(None),
        current_user: UserModel = Depends(get_current_user)
):
    """
    Создает Товар
    """
    db_product = await ProductModel.create(
        **request_schema.model_dump(),
        seller_id=current_user.id
    )

    db_images = []

    for pos, image in enumerate(images):
        file_content = await image.read()
        original_filename = image.filename
        filename = generate_product_image_filename(
            user_id=current_user.id,
            product_id=db_product.id,
            original_filename=original_filename
        )
        image_url = generate_storage_url(filename=filename)

        await s3_storage.upload_file(
            file_path=None,
            file_content=file_content,
            file_name=filename
        )

        db_image = await ImageModel.create(
            product_id=db_product.id,
            url=image_url,
            is_main=True if pos == 0 else False
        )
        db_images.append(db_image)

    return ProductSchema(
        **db_product.__dict__,
        images=db_images
    )


@router.post('/{product_id}/images', response_model=ProductSchema, status_code=status.HTTP_201_CREATED)
async def add_product_images(
        product_id: int,
        images: List[UploadFile] = File(None),
        current_user: UserModel = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_db)
):
    db_product = await session.scalar(
        select(ProductModel)
        .where(ProductModel.id == product_id)
        .options(selectinload(ProductModel.images))
    )

    if not db_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Product not found')

    if db_product.seller_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='The user is not the owner of the product')

    for image in images:
        file_content = await image.read()
        original_filename = image.filename
        filename = generate_product_image_filename(
            user_id=current_user.id,
            product_id=db_product.id,
            original_filename=original_filename
        )
        image_url = generate_storage_url(filename=filename)

        await s3_storage.upload_file(
            file_path=None,
            file_content=file_content,
            file_name=filename
        )

        await ImageModel.create(
            product_id=db_product.id,
            url=image_url
        )

    await session.refresh(db_product)
    return db_product


@router.get('/all/', response_model=List[ProductSchema])
async def get_all_products(session: AsyncSession = Depends(get_async_db)):
    """
    Возвращает все товары
    """
    result = await session.scalars(
        select(ProductModel)
        .where(ProductModel.is_active == True)
        .options(
            selectinload(ProductModel.images)
        )
    )
    db_products = result.all()
    return db_products


@router.get('/my', response_model=List[ProductSchema])
async def get_my_products(
        current_user: UserModel = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_db)
):
    """
    Возвращает товары пользователя
    """
    db_my_products = await session.scalars(
        select(ProductModel)
        .where(ProductModel.seller_id == current_user.id)
        .options(selectinload(ProductModel.images))
    )

    return db_my_products.all()


@router.get('/{product_id}', response_model=ProductSchema)
async def get_product_per_id(product_id: int, session: AsyncSession = Depends(get_async_db)):
    """
    Возвращает товар по его id
    """
    db_product = await session.scalar(
        select(ProductModel)
        .where(ProductModel.id == product_id)
        .options(selectinload(ProductModel.images))
    )

    if not db_product or not db_product.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Product not found')

    return db_product


@router.put('/{product_id}', response_model=ProductSchema)
async def update_product(
    product_id: int,
    request_schema: ProductCreate = Depends(ProductCreate),
    current_user: UserModel = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_db)
):
    """
    Обновление товара по его id
    """
    db_product = await session.scalar(
        select(ProductModel)
        .where(ProductModel.id == product_id)
        .options(selectinload(ProductModel.images))
    )

    if not db_product or not db_product.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Product not found')

    if db_product.seller_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User cannot update product')

    db_product.name = request_schema.name
    db_product.description = request_schema.description
    db_product.price = request_schema.price

    await session.commit()
    await session.refresh(db_product)

    return db_product


@router.patch('/{product_id}/images/{image_id}/main', response_model=ProductSchema)
async def set_main_product_image(
        product_id: int,
        image_id: int,
        current_user: UserModel = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_db)
):
    db_product = await session.scalar(
        select(ProductModel)
        .where(ProductModel.id == product_id)
        .options(selectinload(ProductModel.images))
    )

    if not db_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Product not found')

    if db_product.seller_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='The user cannot set main image of this product'
        )

    db_image = await session.scalar(select(ImageModel).where(ImageModel.id == image_id))

    if not db_image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Image not found')

    if db_image.product_id != db_product.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='The image does not belong to this product')

    for image in db_product.images:
        image.is_main = True if image.id == image_id else False

    await session.commit()
    await session.refresh(db_product)

    return db_product



@router.delete('/{product_id}')
async def delete_product(
        product_id: int,
        current_user: UserModel = Depends(get_current_user)
):
    db_product = await ProductModel.get(product_id)

    if not db_product or not db_product.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Product not found')

    if db_product.seller_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User cannot delete product')

    db_product.is_active = False
    await db_product.save()

    return {'message': 'Product removed successfully'}


@router.delete('/{product_id}/images/{image_id}', response_model=ProductSchema)
async def delete_product_image(
        product_id: int,
        image_id: int,
        current_user: UserModel = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_db)
):
    db_product = await session.scalar(
        select(ProductModel)
        .where(ProductModel.id == product_id)
        .options(selectinload(ProductModel.images))
    )

    if not db_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Product not found')

    if db_product.seller_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='The user cannot delete the image of this product'
        )

    db_image = await session.scalar(select(ImageModel).where(ImageModel.id == image_id))

    if not db_image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Image not found')

    if db_image.product_id != db_product.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='The image does not belong to this product')

    if len(db_product.images) == 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='The product must have at least one image')

    photo_filename = db_image.url.split('/')[-1] if db_image.url else None

    if photo_filename:
        await s3_storage.delete_file(object_name=photo_filename)

    if db_image.is_main:
        for image in db_product.images:
            if image.id != image_id:
                image.is_main = True
                break

    await session.delete(db_image)
    await session.commit()
    await session.refresh(db_product)

    return db_product


@router.get('/search/', response_model=PaginatedResponse)
async def search_product_by_query(
        query: str,
        limit: int = Query(10, ge=1, le=100, description='Размер страницы'),
        offset: int = Query(0, ge=0, description='Смещение следующей страницы'),
        session: AsyncSession = Depends(get_async_db)
):
    response = PRODUCTS_SEARCHER.search_cards(query=query, count=limit, offset=offset)
    ids = list(map(int, response.card_ids))

    if not ids:
        return PaginatedResponse(
            items=[],
            total_count=response.total_count,
            limit=limit,
            next_page_offset=response.next_card_offset
        )

    order = case({id_: index for index, id_ in enumerate(ids)}, value=ProductModel.id)
    stmt = (select(ProductModel)
    .where(
        ProductModel.id.in_(ids)
    ).options(
        selectinload(ProductModel.images)
    ).order_by(order))
    db_products = (await session.scalars(stmt)).all()

    return PaginatedResponse(
        items=db_products,
        total_count=response.total_count,
        limit=limit,
        next_page_offset=response.next_card_offset
    )


@router.get('/', response_model=PaginatedResponse)
async def paginated_products(
        limit: int = Query(10, ge=1, le=100, description='Размер страницы'),
        offset: int = Query(0, ge=0, description='Смещение следующей страницы'),
        session: AsyncSession = Depends(get_async_db)
):
    db_products = (await session.scalars(
        select(ProductModel)
        .where(ProductModel.is_active == True)
        .options(selectinload(ProductModel.images))
    )).all()

    if not db_products:
        return PaginatedResponse(
            items=[],
            total_count=0,
            limit=limit,
            next_page_offset=None
        )

    total_count = len(db_products)
    items = db_products[offset:offset + limit] if offset + limit < total_count else db_products[offset:]
    next_page_offset = offset + limit if offset + limit < total_count else None

    return PaginatedResponse(
        items=items,
        total_count=total_count,
        limit=limit,
        next_page_offset=next_page_offset
    )



@router.get('/update-es/')
async def update_es():
    updater = ESUpdateProductsService(es=ES)
    await updater.update_products()
    return {'message': 'OK'}