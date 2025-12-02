from fastapi import APIRouter, status, Depends
from faststream.rabbit.fastapi import RabbitRouter

from src.api.api_services.purchase_api_services import (
    AddPurchaseAPIService,
    UpdatePurchaseAPIService,
    GetPurchaseAPIService,
)
from src.config import RABBITMQ_URL
from src.api.schemas.purchases import PurchaseSchema, PurchaseCreate

router = APIRouter(prefix="/purchases", tags=["purchases"])
rabbit_router = RabbitRouter(url=RABBITMQ_URL, prefix="/purchases", tags=["purchases"])


@router.get("/{purchase_id}", response_model=PurchaseSchema)
async def get_purchase(
    purchase_id: int, get_purchase_api_service: GetPurchaseAPIService = Depends()
):
    return await get_purchase_api_service.exec(purchase_id=purchase_id)


@rabbit_router.post(
    "/", response_model=PurchaseSchema, status_code=status.HTTP_201_CREATED
)
async def create_purchase(
    purchase: PurchaseCreate,
    add_purchase_api_service: AddPurchaseAPIService = Depends(),
):
    purchase = await add_purchase_api_service.exec(
        product_id=purchase.product_id, comment=purchase.comment
    )
    await rabbit_router.broker.publish(f"{purchase.id}", queue="create_purchases")
    return purchase


@rabbit_router.patch("/accept/{purchase_id}", response_model=PurchaseSchema)
async def accept_purchase(
    purchase_id: int,
    update_purchase_api_service: UpdatePurchaseAPIService = Depends(),
):
    purchase = await update_purchase_api_service.exec(
        purchase_id=purchase_id, p_status="accept"
    )
    await rabbit_router.broker.publish(f"{purchase.id}", queue="accept_purchases")
    return purchase


@rabbit_router.patch("/reject/{purchase_id}", response_model=PurchaseSchema)
async def reject_purchase(
    purchase_id: int,
    update_purchase_api_service: UpdatePurchaseAPIService = Depends(),
):
    purchase = await update_purchase_api_service.exec(
        purchase_id=purchase_id, p_status="reject"
    )
    await rabbit_router.broker.publish(f"{purchase.id}", queue="reject_purchases")
    return purchase
