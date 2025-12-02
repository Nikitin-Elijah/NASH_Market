import pytest
from src.services.review_services import AddReviewService, GetAboutUserReviewsService
from src.exceptions.purchase_exceptions import (
    PurchaseNotYetCompleteException,
    UserDidNotParticipateInPurchaseException,
)
from src.exceptions.review_exceptions import UserAlreadyLeftReviewForSellerException
from .conftest import FakeUser, FakePurchase, FakeReview


@pytest.mark.asyncio
async def test_add_review_success(
    mock_session,
    mock_get_purchase_service,
    mock_recalculate_user_rating_service,
    mock_check_review_service,
):
    user = FakeUser(id=1)
    purchase = FakePurchase(id=10, buyer_id=1, seller_id=2)

    mock_check_review_service.exec.return_value = None
    mock_get_purchase_service.exec.return_value = purchase

    service = AddReviewService(
        user=user,
        session=mock_session,
        get_purchase_service=mock_get_purchase_service,
        recalculate_user_rating_service=mock_recalculate_user_rating_service,
        check_review_service=mock_check_review_service,
    )

    review = await service.exec(purchase_id=10, text="Good seller", rating=5)

    assert review.author_id == 1
    assert review.recipient_id == 2
    assert review.text == "Good seller"
    mock_recalculate_user_rating_service.exec.assert_awaited_once_with(user_id=2)


@pytest.mark.asyncio
async def test_add_review_purchase_not_complete(
    mock_session,
    mock_get_purchase_service,
    mock_recalculate_user_rating_service,
    mock_check_review_service,
):
    user = FakeUser(id=1)
    purchase = FakePurchase(id=10, buyer_id=1, seller_id=2, successful=False)

    mock_get_purchase_service.exec.return_value = purchase

    service = AddReviewService(
        user=user,
        session=mock_session,
        get_purchase_service=mock_get_purchase_service,
        recalculate_user_rating_service=mock_recalculate_user_rating_service,
        check_review_service=mock_check_review_service,
    )

    with pytest.raises(PurchaseNotYetCompleteException):
        await service.exec(purchase_id=10, text="test", rating=5)


@pytest.mark.asyncio
async def test_add_review_user_not_participant(
    mock_session,
    mock_get_purchase_service,
    mock_recalculate_user_rating_service,
    mock_check_review_service,
):
    user = FakeUser(id=1)
    purchase = FakePurchase(id=10, buyer_id=99, seller_id=2)

    mock_get_purchase_service.exec.return_value = purchase

    service = AddReviewService(
        user=user,
        session=mock_session,
        get_purchase_service=mock_get_purchase_service,
        recalculate_user_rating_service=mock_recalculate_user_rating_service,
        check_review_service=mock_check_review_service,
    )

    with pytest.raises(UserDidNotParticipateInPurchaseException):
        await service.exec(purchase_id=10, text="test", rating=5)


@pytest.mark.asyncio
async def test_add_review_already_exists(
    mock_session,
    mock_get_purchase_service,
    mock_recalculate_user_rating_service,
    mock_check_review_service,
):
    user = FakeUser(id=1)
    purchase = FakePurchase(id=10, buyer_id=1, seller_id=2)
    existing_review = FakeReview(
        id=100, author_id=1, recipient_id=2, text="old", rating=5
    )

    mock_get_purchase_service.exec.return_value = purchase
    mock_session.scalar.return_value = existing_review

    service = AddReviewService(
        user=user,
        session=mock_session,
        get_purchase_service=mock_get_purchase_service,
        recalculate_user_rating_service=mock_recalculate_user_rating_service,
        check_review_service=mock_check_review_service,
    )

    with pytest.raises(UserAlreadyLeftReviewForSellerException):
        await service.exec(purchase_id=10, text="test", rating=5)


@pytest.mark.asyncio
async def test_get_reviews_about_user(mock_session, mock_get_user_service):
    reviews = [FakeReview(id=1, author_id=2, recipient_id=1, text="good", rating=5)]
    user = FakeUser(id=1, received_reviews=reviews)

    mock_get_user_service.exec.return_value = user

    service = GetAboutUserReviewsService(
        session=mock_session, get_user_service=mock_get_user_service
    )

    result = await service.exec(user_id=1)
    assert result == reviews
