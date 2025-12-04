from fastapi import APIRouter, status, Depends

from src.api.api_services.review_api_services import (
    AddReviewAPIService,
    GetAboutUserReviewsAPIService,
)
from src.api.schemas.reviews import ReviewSchema, ReviewCreate


router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("", response_model=ReviewSchema, status_code=status.HTTP_201_CREATED)
async def create_review(
    review: ReviewCreate,
    add_review_api_service: AddReviewAPIService = Depends(),
):
    return await add_review_api_service.exec(
        purchase_id=review.purchase_id, text=review.text, rating=review.rating
    )


@router.get("/{user_id}", response_model=list[ReviewSchema])
async def get_review_about_user(
    user_id: int,
    get_about_user_reviews_api_service: GetAboutUserReviewsAPIService = Depends(),
):
    return await get_about_user_reviews_api_service.exec(user_id=user_id)
