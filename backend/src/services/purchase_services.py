from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import get_current_user
from src.database.db_depends import get_async_db
from src.exceptions.purchase_exceptions import (
    PurchaseNotFoundException,
    CannotBuyOwnProductException,
    PurchaseRequestAlreadyExistsException,
    UserCannotAcceptPurchaseException,
    PurchaseAlreadyProcessedException, UserCannotCompletePurchaseException,
)
from src.models import UserModel, PurchaseModel, ProductModel
from src.services.product_services import GetProductService


class GetPurchaseService:
    def __init__(
        self,
        session: AsyncSession = Depends(get_async_db),
    ):
        self.session = session

    async def _get_purchase(self, purchase_id: int) -> PurchaseModel | None:
        purchase = await self.session.scalar(
            select(PurchaseModel).where(PurchaseModel.id == purchase_id)
        )
        return purchase

    @staticmethod
    def _validate(purchase: PurchaseModel | None):
        if not purchase:
            raise PurchaseNotFoundException("Purchase not found")

    async def exec(self, purchase_id: int) -> PurchaseModel:
        purchase = await self._get_purchase(purchase_id=purchase_id)
        self._validate(purchase=purchase)
        return purchase


class AddPurchaseService:
    def __init__(
        self,
        user: UserModel = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_db),
        get_product_service: GetProductService = Depends(),
    ):
        self.user = user
        self.session = session
        self.get_product_service = get_product_service

    async def _add_purchase(self, product: ProductModel, comment: str) -> PurchaseModel:
        purchase = PurchaseModel(
            product_id=product.id,
            seller_id=product.seller_id,
            buyer_id=self.user.id,
            comment=comment,
        )
        self.session.add(purchase)
        await self.session.commit()
        await self.session.refresh(purchase)
        return purchase

    async def _validate(self, product: ProductModel):
        if product.seller_id == self.user.id:
            raise CannotBuyOwnProductException("You cannot purchase your own product")
        db_purchase = await self.session.scalar(
            select(PurchaseModel).where(
                PurchaseModel.product_id == product.id,
                PurchaseModel.buyer_id == self.user.id,
            )
        )
        if db_purchase:
            raise PurchaseRequestAlreadyExistsException(
                "Purchase request for this product already exists for this user"
            )

    async def exec(self, product_id: int, comment: str) -> PurchaseModel:
        product = await self.get_product_service.exec(product_id=product_id)
        await self._validate(product=product)
        purchase = await self._add_purchase(product=product, comment=comment)
        return purchase


class UpdatePurchaseService:
    def __init__(
        self,
        user: UserModel = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_db),
        get_purchase_service: GetPurchaseService = Depends(),
    ):
        self.user = user
        self.session = session
        self.get_purchase_service = get_purchase_service

    async def _update_purchase(self, purchase: PurchaseModel, p_status: str) -> PurchaseModel:
        if p_status == "accept":
            purchase.permission = True
        elif p_status == "reject":
            purchase.refusal = True
        await self.session.commit()
        await self.session.refresh(purchase)
        return purchase

    def _validate(self, purchase: PurchaseModel):
        if purchase.seller_id != self.user.id:
            raise UserCannotAcceptPurchaseException("User can not process purchase")
        if purchase.permission:
            raise PurchaseAlreadyProcessedException("Purchase already accepted")
        if purchase.refusal:
            raise PurchaseAlreadyProcessedException("Purchase already rejected")

    async def exec(self, purchase_id: int, p_status: str) -> PurchaseModel:
        purchase = await self.get_purchase_service.exec(purchase_id=purchase_id)
        self._validate(purchase=purchase)
        return await self._update_purchase(purchase=purchase, p_status=p_status)


class CompletePurchaseService:
    def __init__(
        self,
        session: AsyncSession = Depends(get_async_db),
        user: UserModel = Depends(get_current_user),
        get_purchase_service: GetPurchaseService = Depends()
    ):
        self.session = session
        self.user = user
        self.get_purchase_service = get_purchase_service

    async def _complete_purchase(self, purchase) -> PurchaseModel:
        purchase.successful = True
        await self.session.commit()
        await self.session.refresh(purchase)
        return purchase

    def _validate(self, purchase: PurchaseModel):
        if purchase.seller_id != self.user.id:
            raise UserCannotCompletePurchaseException("User can not process purchase")
        if not purchase.permission:
            raise UserCannotCompletePurchaseException("Purchase is not accepted")
        if purchase.successful:
            raise PurchaseAlreadyProcessedException("Purchase already complete")

    async def exec(self, purchase_id: int) -> PurchaseModel:
        purchase = await self.get_purchase_service.exec(purchase_id=purchase_id)
        self._validate(purchase=purchase)
        return await self._complete_purchase(purchase=purchase)
