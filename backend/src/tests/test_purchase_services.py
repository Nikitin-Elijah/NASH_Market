import pytest
from src.services.purchase_services import (
    GetPurchaseService,
    AddPurchaseService,
    UpdatePurchaseService,
)
from src.exceptions.purchase_exceptions import (
    PurchaseNotFoundException,
    CannotBuyOwnProductException,
    PurchaseRequestAlreadyExistsException,
    UserCannotAcceptPurchaseException,
    PurchaseAlreadyProcessedException,
)
from src.tests.conftest import FakePurchase, FakeUser, FakeProductForPurchase


# ------------------------------
# GetPurchaseService
# ------------------------------


@pytest.mark.asyncio
async def test_get_purchase_success(mock_session):
    fake_purchase = FakePurchase()
    mock_session.scalar.return_value = fake_purchase

    service = GetPurchaseService(session=mock_session)
    purchase = await service.exec(purchase_id=1)

    assert purchase == fake_purchase
    mock_session.scalar.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_purchase_not_found(mock_session):
    mock_session.scalar.return_value = None
    service = GetPurchaseService(session=mock_session)

    with pytest.raises(PurchaseNotFoundException):
        await service.exec(purchase_id=1)


# ------------------------------
# AddPurchaseService
# ------------------------------


@pytest.mark.asyncio
async def test_add_purchase_success(
    mock_session, fake_user, mock_get_product_service_for_purchase
):
    fake_product = FakeProductForPurchase(id=1, seller_id=10)
    mock_get_product_service_for_purchase.exec.return_value = fake_product

    mock_session.scalar.return_value = None

    service = AddPurchaseService(
        user=fake_user,
        session=mock_session,
        get_product_service=mock_get_product_service_for_purchase,
    )
    purchase = await service.exec(product_id=1, comment="Nice product")

    assert purchase.product_id == fake_product.id
    assert purchase.buyer_id == fake_user.id
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_add_purchase_own_product(
    mock_session, fake_user, mock_get_product_service_for_purchase
):
    fake_product = FakeProductForPurchase(id=1, seller_id=fake_user.id)
    mock_get_product_service_for_purchase.exec.return_value = fake_product

    service = AddPurchaseService(
        user=fake_user,
        session=mock_session,
        get_product_service=mock_get_product_service_for_purchase,
    )

    with pytest.raises(CannotBuyOwnProductException):
        await service.exec(product_id=1, comment="Own product")


@pytest.mark.asyncio
async def test_add_purchase_already_exists(
    mock_session, fake_user, mock_get_product_service_for_purchase
):
    fake_product = FakeProductForPurchase(id=1, seller_id=10)
    mock_get_product_service_for_purchase.exec.return_value = fake_product
    mock_session.scalar.return_value = FakePurchase()  # уже есть заявка

    service = AddPurchaseService(
        user=fake_user,
        session=mock_session,
        get_product_service=mock_get_product_service_for_purchase,
    )

    with pytest.raises(PurchaseRequestAlreadyExistsException):
        await service.exec(product_id=1, comment="Duplicate purchase")


# ------------------------------
# UpdatePurchaseService
# ------------------------------


@pytest.mark.asyncio
async def test_update_purchase_accept_success(
    mock_session, fake_user, mock_get_purchase_service_for_update
):
    fake_purchase = FakePurchase(seller_id=fake_user.id)
    mock_get_purchase_service_for_update.exec.return_value = fake_purchase

    service = UpdatePurchaseService(
        user=fake_user,
        session=mock_session,
        get_purchase_service=mock_get_purchase_service_for_update,
    )

    updated_purchase = await service.exec(purchase_id=1, p_status="accept")
    assert updated_purchase.permission is True
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_purchase_reject_success(
    mock_session, fake_user, mock_get_purchase_service_for_update
):
    fake_purchase = FakePurchase(seller_id=fake_user.id)
    mock_get_purchase_service_for_update.exec.return_value = fake_purchase

    service = UpdatePurchaseService(
        user=fake_user,
        session=mock_session,
        get_purchase_service=mock_get_purchase_service_for_update,
    )

    updated_purchase = await service.exec(purchase_id=1, p_status="reject")
    assert updated_purchase.refusal is True
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_purchase_invalid_user(
    mock_session, fake_user, mock_get_purchase_service_for_update
):
    fake_purchase = FakePurchase(seller_id=999)  # другой пользователь
    mock_get_purchase_service_for_update.exec.return_value = fake_purchase

    service = UpdatePurchaseService(
        user=fake_user,
        session=mock_session,
        get_purchase_service=mock_get_purchase_service_for_update,
    )

    with pytest.raises(UserCannotAcceptPurchaseException):
        await service.exec(purchase_id=1, p_status="accept")


@pytest.mark.asyncio
async def test_update_purchase_already_processed(
    mock_session, fake_user, mock_get_purchase_service_for_update
):
    fake_purchase = FakePurchase(seller_id=fake_user.id, permission=True)
    mock_get_purchase_service_for_update.exec.return_value = fake_purchase

    service = UpdatePurchaseService(
        user=fake_user,
        session=mock_session,
        get_purchase_service=mock_get_purchase_service_for_update,
    )

    with pytest.raises(PurchaseAlreadyProcessedException):
        await service.exec(purchase_id=1, p_status="accept")
