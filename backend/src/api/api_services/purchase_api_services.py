from fastapi import Depends, HTTPException, status

from src.exceptions.product_exceptions import ProductNotFoundException
from src.exceptions.purchase_exceptions import (
    CannotBuyOwnProductException,
    PurchaseRequestAlreadyExistsException,
    PurchaseNotFoundException,
    UserCannotAcceptPurchaseException,
    PurchaseAlreadyProcessedException,
)
from src.models import PurchaseModel
from src.services.purchase_services import AddPurchaseService, UpdatePurchaseService, GetPurchaseService


class GetPurchaseAPIService:
    """
    API Сервис для получения записи о покупке по id
    """
    def __init__(self, get_purchase_service: GetPurchaseService = Depends(GetPurchaseService)):
        self.get_purchase_service = get_purchase_service

    async def exec(self, purchase_id: int) -> PurchaseModel:
        try:
            return await self.get_purchase_service.exec(purchase_id=purchase_id)
        except PurchaseNotFoundException as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


class AddPurchaseAPIService:
    """
    API Сервис для создания предложения о покупке
    """

    def __init__(
        self, add_purchase_service: AddPurchaseService = Depends(AddPurchaseService)
    ):
        self.add_purchase_service = add_purchase_service

    async def exec(self, product_id: int, comment: str) -> PurchaseModel:
        try:
            return await self.add_purchase_service.exec(
                product_id=product_id, comment=comment
            )
        except ProductNotFoundException as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except CannotBuyOwnProductException as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except PurchaseRequestAlreadyExistsException as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


class UpdatePurchaseAPIService:
    """
    API Сервис для обновления статуса предложения о покупке
    """

    def __init__(
        self,
        update_purchase_service: UpdatePurchaseService = Depends(UpdatePurchaseService),
    ):
        self.update_purchase_service = update_purchase_service

    async def exec(self, purchase_id: int, p_status: str) -> PurchaseModel:
        try:
            return await self.update_purchase_service.exec(
                purchase_id=purchase_id, p_status=p_status
            )
        except PurchaseNotFoundException as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except UserCannotAcceptPurchaseException as e:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
        except PurchaseAlreadyProcessedException as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
