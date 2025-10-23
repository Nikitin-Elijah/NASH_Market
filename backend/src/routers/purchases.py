import json

from fastapi import APIRouter, status, Depends, HTTPException
from faststream.rabbit.fastapi import RabbitRouter

from src.auth import get_current_user
from src.config import RABBITMQ_URL
from src.models import UserModel, ProductModel
from src.models.purchases import PurchaseModel
from src.schemas.purchases import PurchaseSchema, PurchaseCreate

router = APIRouter(prefix='/purchases', tags=['purchases'])
rabbit_router = RabbitRouter(url=RABBITMQ_URL, prefix='/purchases', tags=['purchases'])


@rabbit_router.post('/', response_model=PurchaseSchema, status_code=status.HTTP_201_CREATED)
async def create_purchase(purchase: PurchaseCreate, current_user: UserModel = Depends(get_current_user)):
    db_product = await ProductModel.get(purchase.product_id)

    if not db_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Product not found')

    if db_product.seller_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot purchase your own product"
        )

    db_purchases = await PurchaseModel.filter(product_id=purchase.product_id, buyer_id=current_user.id)

    if db_purchases:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Purchase request for this product already exists for this user'
        )

    db_purchase = await PurchaseModel.create(
        product_id=purchase.product_id,
        seller_id=db_product.seller_id,
        buyer_id=current_user.id,
        comment=purchase.comment
    )

    await rabbit_router.broker.publish(f'{db_purchase.id}', queue="create_purchases")

    return db_purchase


@rabbit_router.patch('/accept/{purchase_id}', response_model=PurchaseSchema)
async def accept_purchase(purchase_id: int, current_user: UserModel = Depends(get_current_user)):
    db_purchase = await PurchaseModel.get(purchase_id)

    if not db_purchase:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Purchase not found')

    if db_purchase.seller_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User can not accept purchase')

    if db_purchase.permission:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Purchase already accepted')

    if db_purchase.refusal:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Purchase already rejected')

    db_purchase.permission = True
    await db_purchase.save()

    await rabbit_router.broker.publish(f'{db_purchase.id}', queue="accept_purchases")

    return db_purchase


@rabbit_router.patch('/reject/{purchase_id}', response_model=PurchaseSchema)
async def accept_purchase(purchase_id: int, current_user: UserModel = Depends(get_current_user)):
    db_purchase = await PurchaseModel.get(purchase_id)

    if not db_purchase:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Purchase not found')

    if db_purchase.seller_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User can not reject purchase')

    if db_purchase.permission:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Purchase already accepted')

    if db_purchase.refusal:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Purchase already rejected')

    db_purchase.refusal = True
    await db_purchase.save()

    await rabbit_router.broker.publish(f'{db_purchase.id}', queue="reject_purchases")

    return db_purchase