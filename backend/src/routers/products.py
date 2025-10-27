from typing import List

from fastapi import APIRouter, status, Form, UploadFile, Depends, HTTPException
from sqlalchemy import select, update, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.auth import get_current_user
from src.config import s3_storage, PRODUCTS_SEARCHER, ES
from src.database.db_depends import get_async_db
from src.models import UserModel, ProductModel
from src.schemas.products import ProductSchema, ProductCreate
from src.search_service.es_update_products_service import ESUpdateProductsService
from src.utils import generate_product_image_filename, generate_storage_url

router = APIRouter(prefix='/products', tags=['products'])


@router.post('/', response_model=ProductSchema, status_code=status.HTTP_201_CREATED)
async def create_product(
        request_schema: ProductCreate = Depends(ProductCreate),
        image: UploadFile | None = None,
        current_user: UserModel = Depends(get_current_user)
):
    """
    Создает Товар
    """
    db_product = await ProductModel.create(
        **request_schema.model_dump(),
        image_url='default_url',
        rating=5,
        seller_id=current_user.id
    )

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

    db_product.image_url = image_url
    await db_product.save()

    return db_product


@router.get('/', response_model=List[ProductSchema])
async def get_all_products():
    """
    Возвращает все товары
    """
    return await ProductModel.all()


@router.get('/my', response_model=List[ProductSchema])
async def get_my_products(
        current_user: UserModel = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_db)
):
    """
    Возвращает товары пользователя
    """
    user = await session.scalar(
        select(UserModel)
        .options(selectinload(UserModel.products))
        .where(UserModel.id == current_user.id)
    )

    return user.products


@router.get('/{product_id}', response_model=ProductSchema)
async def get_product_per_id(product_id: int):
    db_product = await ProductModel.get(product_id)

    if not db_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Product not found')

    return db_product


@router.put('/{product_id}', response_model=ProductSchema)
async def update_product(
        product_id: int,
        name: str = Form(...),
        description: str = Form(...),
        price: float = Form(...),
        image: UploadFile | None = None,
        current_user: UserModel = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_db)
):
    """
    Обновление товара по его id
    """
    db_product = await ProductModel.get(product_id)

    if not db_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Product not found')

    if db_product.seller_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User cannot update product')

    update_product_data = ProductCreate(name=name, description=description, price=price)

    if image:
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

        old_photo_filename = db_product.image_url.split('/')[-1] if db_product.image_url else None
        db_product.image_url = image_url
        await db_product.save()

        if old_photo_filename:
            await s3_storage.delete_file(object_name=old_photo_filename)

    await session.execute(
        update(ProductModel).where(
            ProductModel.id == db_product.id
        ).values(
            **update_product_data.model_dump()
        )
    )
    await session.commit()

    return db_product


@router.delete('/{product_id}')
async def delete_product(
        product_id: int,
        current_user: UserModel = Depends(get_current_user)
):
    db_product = await ProductModel.get(product_id)

    if not db_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Product not found')

    if db_product.seller_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User cannot delete product')

    old_photo_filename = db_product.image_url.split('/')[-1] if db_product.image_url else None

    if old_photo_filename:
        await s3_storage.delete_file(object_name=old_photo_filename)

    await db_product.delete()
    return {'message': 'Product removed successfully'}


@router.get('/search/', response_model=List[ProductSchema])
async def search_product_by_query(
    query: str,
    limit: int = 20,
    offset: int = 0,
    session: AsyncSession = Depends(get_async_db)
):
    products = PRODUCTS_SEARCHER.search_cards(query=query, count=limit, offset=offset)
    ids = list(map(int, products.card_ids))

    if not ids:
        return []

    order = case({id_: index for index, id_ in enumerate(ids)}, value=ProductModel.id)
    stmt = select(ProductModel).where(ProductModel.id.in_(ids)).order_by(order)
    db_products = (await session.scalars(stmt)).all()

    return db_products


@router.get('/update-es/')
async def update_es():
    updater = ESUpdateProductsService(es=ES)
    await updater.update_products()
    return {'message': 'OK'}