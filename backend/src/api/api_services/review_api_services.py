from fastapi import Depends, HTTPException, status

from src.cache.cache import redis_cache, cache_delete_prefix
from src.exceptions.purchase_exceptions import (
    PurchaseNotFoundException,
    PurchaseNotYetCompleteException,
    UserDidNotParticipateInPurchaseException,
)
from src.exceptions.review_exceptions import UserAlreadyLeftReviewForSellerException
from src.exceptions.user_exceptions import UserNotFoundException
from src.models import ReviewModel
from src.services.review_services import AddReviewService, GetAboutUserReviewsService


class AddReviewAPIService:
    """
    API Сервис для создания отзыва после покупки
    """

    def __init__(self, add_review_service: AddReviewService = Depends()):
        self.add_review_service = add_review_service

    async def exec(self, purchase_id: int, text: str, rating: int) -> ReviewModel:
        try:
            await cache_delete_prefix(prefix='reviews')
            return await self.add_review_service.exec(
                purchase_id=purchase_id, text=text, rating=rating
            )
        except PurchaseNotFoundException as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except PurchaseNotYetCompleteException as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except UserDidNotParticipateInPurchaseException as e:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
        except UserAlreadyLeftReviewForSellerException as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


class GetAboutUserReviewsAPIService:
    """
    API Сервис для получения отзывов о пользователе
    """

    def __init__(
        self,
        get_about_user_reviews_service: GetAboutUserReviewsService = Depends(

        ),
    ):
        self.get_about_user_reviews_service = get_about_user_reviews_service

    @redis_cache(prefix='reviews', ttl=1200)
    async def exec(self, user_id: int) -> list[ReviewModel]:
        try:
            return await self.get_about_user_reviews_service.exec(user_id=user_id)
        except UserNotFoundException as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
