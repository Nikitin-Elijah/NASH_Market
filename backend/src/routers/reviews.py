from typing import List

from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from src.auth import get_current_user
from src.config import database_configuration
from src.models import UserModel, PurchaseModel, ReviewModel
from src.schemas.reviews import ReviewSchema, ReviewCreate

router = APIRouter(prefix='/reviews', tags=['reviews'])


@router.post('/', response_model=ReviewSchema, status_code=status.HTTP_201_CREATED)
async def create_review(review: ReviewCreate, current_user: UserModel = Depends(get_current_user)):
    db_purchase = await PurchaseModel.get(review.purchase_id)

    if not db_purchase:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Purchase not found')

    if not db_purchase.successful:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='The purchase is not yet complete')

    if db_purchase.buyer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail='The user did not participate in this purchase'
        )

    db_reviews = await ReviewModel.filter(author_id=current_user.id, recipient_id=db_purchase.seller_id)

    if db_reviews:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='The user has already left a review for this seller'
        )

    db_review = await ReviewModel.create(
        author_id=current_user.id,
        recipient_id=db_purchase.seller_id,
        purchase_id=review.purchase_id,
        rating=review.rating,
        text=review.text
    )

    async with database_configuration.async_session_maker() as session:
        db_seller = await session.scalar(
            select(UserModel)
            .options(selectinload(UserModel.received_reviews))
            .where(UserModel.id == db_purchase.seller_id)
        )

        update_seller_rating = sum([r.rating for r in db_seller.received_reviews]) / len(db_seller.received_reviews)

        await session.execute(
            update(UserModel).where(UserModel.id == db_seller.id).values(rating=update_seller_rating)
        )
        await session.commit()

    return db_review


@router.get('/{user_id}', response_model=List[ReviewSchema])
async def get_review_about_user(user_id: int):
    db_reviews = await ReviewModel.filter(recipient_id=user_id)
    return db_reviews