from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import get_current_user
from src.database.db_depends import get_async_db
from src.exceptions.purchase_exceptions import (
    PurchaseNotYetCompleteException,
    UserDidNotParticipateInPurchaseException,
)
from src.exceptions.review_exceptions import UserAlreadyLeftReviewForSellerException
from src.models import UserModel, ReviewModel, PurchaseModel
from src.services.purchase_services import GetPurchaseService
from src.services.user_services import RecalculateUserRatingService, GetUserService


class CheckReviewService:
    def __init__(self, session: AsyncSession = Depends(get_async_db)):
        self.session = session

    async def _check_review(
        self, author_id: int, recipient_id: int
    ) -> ReviewModel | None:
        review = await self.session.scalar(
            select(ReviewModel).where(
                ReviewModel.author_id == author_id,
                ReviewModel.recipient_id == recipient_id,
            )
        )
        return review

    async def exec(self, author_id: int, recipient_id: int) -> ReviewModel | None:
        return await self._check_review(author_id=author_id, recipient_id=recipient_id)


class AddReviewService:
    def __init__(
        self,
        user: UserModel = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_db),
        get_purchase_service: GetPurchaseService = Depends(),
        recalculate_user_rating_service: RecalculateUserRatingService = Depends(),
        check_review_service: CheckReviewService = Depends(),
    ):
        self.user = user
        self.session = session
        self.get_purchase_service = get_purchase_service
        self.recalculate_user_rating_service = recalculate_user_rating_service
        self.check_review_service = check_review_service

    async def _add_review(
        self, purchase: PurchaseModel, text: str, rating: int
    ) -> ReviewModel:
        review = ReviewModel(
            author_id=self.user.id,
            recipient_id=purchase.seller_id,
            purchase_id=purchase.id,
            rating=rating,
            text=text,
        )
        self.session.add(review)
        await self.session.commit()
        await self.session.refresh(review)
        return review

    async def _validate(self, purchase: PurchaseModel, review: ReviewModel):
        if not purchase.successful:
            raise PurchaseNotYetCompleteException("The purchase is not yet complete")
        if purchase.buyer_id != self.user.id:
            raise UserDidNotParticipateInPurchaseException(
                "The user did not participate in this purchase"
            )
        if review:
            raise UserAlreadyLeftReviewForSellerException(
                "The user has already left a review for this seller"
            )

    async def exec(self, purchase_id: int, text: str, rating: int) -> ReviewModel:
        purchase = await self.get_purchase_service.exec(purchase_id=purchase_id)
        review = await self.check_review_service.exec(
            author_id=self.user.id, recipient_id=purchase.seller_id
        )
        await self._validate(purchase=purchase, review=review)
        review = await self._add_review(purchase=purchase, text=text, rating=rating)
        await self.recalculate_user_rating_service.exec(user_id=review.recipient_id)
        return review


class GetAboutUserReviewsService:
    def __init__(
        self,
        session: AsyncSession = Depends(get_async_db),
        get_user_service: GetUserService = Depends(),
    ):
        self.session = session
        self.get_user_service = get_user_service

    async def _get_reviews_about_user(self, user: UserModel) -> list[ReviewModel]:
        await self.session.refresh(user, ["received_reviews"])
        return user.received_reviews

    async def exec(self, user_id: int) -> list[ReviewModel]:
        user = await self.get_user_service.exec(user_id=user_id)
        reviews = await self._get_reviews_about_user(user=user)
        return reviews
