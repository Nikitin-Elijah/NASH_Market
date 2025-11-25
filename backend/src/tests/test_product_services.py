import pytest
from unittest.mock import AsyncMock

from src.services.product_services import (
    GetProductService,
    AddProductService,
    AddProductImageService,
    UpdateProductService,
    SwitchMainImageService,
    DeleteProductService,
    DeleteProductImageService,
)

from src.exceptions.product_exceptions import (
    ProductNotFoundException,
    UserIsNotProductOwnerException,
)

from src.exceptions.image_exceptions import ImageNotBelongToProductException

from src.tests.conftest import FakeProduct, FakeUser, FakeImage


# ---------------------------------------------------------
# GetProductService
# ---------------------------------------------------------


@pytest.mark.asyncio
async def test_get_product_success(mock_session):
    product = FakeProduct()
    mock_session.scalar.return_value = product

    service = GetProductService(session=mock_session)

    result = await service.exec(1)

    assert result is product
    mock_session.scalar.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_product_not_found(mock_session):
    mock_session.scalar.return_value = None

    service = GetProductService(session=mock_session)

    with pytest.raises(ProductNotFoundException):
        await service.exec(1)


# ---------------------------------------------------------
# AddProductService
# ---------------------------------------------------------


@pytest.mark.asyncio
async def test_add_product_success(
    mock_session, mock_add_image_service, fake_upload_file
):
    user = FakeUser(id=10)

    mock_add_image_service.exec.return_value = FakeImage(id=1, product_id=1)

    service = AddProductService(
        user=user, session=mock_session, add_image_service=mock_add_image_service
    )

    product = await service.exec(
        name="Test Product", description="Desc", price=100, images=[fake_upload_file]
    )

    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited()
    mock_add_image_service.exec.assert_awaited_once()
    assert product is not None


# ---------------------------------------------------------
# AddProductImageService
# ---------------------------------------------------------


@pytest.mark.asyncio
async def test_add_product_image_success(
    mock_session, mock_get_product_service, mock_add_image_service, fake_upload_file
):
    user = FakeUser(id=10)
    product = FakeProduct(id=1, seller_id=10)

    mock_get_product_service.exec.return_value = product
    mock_add_image_service.exec.return_value = FakeImage(id=1, product_id=1)

    service = AddProductImageService(
        user=user,
        session=mock_session,
        get_product_service=mock_get_product_service,
        add_image_service=mock_add_image_service,
    )

    result = await service.exec(1, [fake_upload_file])

    mock_add_image_service.exec.assert_awaited_once()
    assert result is product


@pytest.mark.asyncio
async def test_add_product_image_not_owner(
    mock_session, mock_get_product_service, fake_upload_file
):
    user = FakeUser(id=99)
    product = FakeProduct(id=1, seller_id=10)

    mock_get_product_service.exec.return_value = product

    service = AddProductImageService(
        user=user,
        session=mock_session,
        get_product_service=mock_get_product_service,
        add_image_service=AsyncMock(),
    )

    with pytest.raises(UserIsNotProductOwnerException):
        await service.exec(1, [fake_upload_file])


# ---------------------------------------------------------
# UpdateProductService
# ---------------------------------------------------------


@pytest.mark.asyncio
async def test_update_product_success(mock_session, mock_get_product_service):
    user = FakeUser(id=10)
    product = FakeProduct(id=1, seller_id=10)

    mock_get_product_service.exec.return_value = product

    service = UpdateProductService(
        user=user, session=mock_session, get_product_service=mock_get_product_service
    )

    updated = await service.exec(1, name="Updated!")

    assert updated.name == "Updated!"
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_product_not_owner(mock_session, mock_get_product_service):
    user = FakeUser(id=99)
    product = FakeProduct(id=1, seller_id=10)

    mock_get_product_service.exec.return_value = product

    service = UpdateProductService(
        user=user, session=mock_session, get_product_service=mock_get_product_service
    )

    with pytest.raises(UserIsNotProductOwnerException):
        await service.exec(1, name="Updated!")


# ---------------------------------------------------------
# SwitchMainImageService
# ---------------------------------------------------------


@pytest.mark.asyncio
async def test_switch_main_image_success(
    mock_session, mock_get_product_service, mock_get_image_service
):
    user = FakeUser(id=10)
    product = FakeProduct(id=1, seller_id=10)
    product.images = [
        FakeImage(id=1, product_id=1, is_main=True),
        FakeImage(id=2, product_id=1, is_main=False),
    ]

    image = FakeImage(id=2, product_id=1)

    mock_get_product_service.exec.return_value = product
    mock_get_image_service.exec.return_value = image

    service = SwitchMainImageService(
        user=user,
        session=mock_session,
        get_product_service=mock_get_product_service,
        get_image_service=mock_get_image_service,
    )

    updated = await service.exec(1, 2)

    assert updated.images[0].is_main is False
    assert updated.images[1].is_main is True


@pytest.mark.asyncio
async def test_switch_main_image_wrong_product(
    mock_session, mock_get_product_service, mock_get_image_service
):
    user = FakeUser(id=10)
    product = FakeProduct(id=1, seller_id=10)
    wrong_image = FakeImage(id=2, product_id=999)

    mock_get_product_service.exec.return_value = product
    mock_get_image_service.exec.return_value = wrong_image

    service = SwitchMainImageService(
        user=user,
        session=mock_session,
        get_product_service=mock_get_product_service,
        get_image_service=mock_get_image_service,
    )

    with pytest.raises(ImageNotBelongToProductException):
        await service.exec(1, 2)


# ---------------------------------------------------------
# DeleteProductService
# ---------------------------------------------------------


@pytest.mark.asyncio
async def test_delete_product_success(mock_session, mock_get_product_service):
    user = FakeUser(id=10)
    product = FakeProduct(id=1, seller_id=10)

    mock_get_product_service.exec.return_value = product

    service = DeleteProductService(
        user=user, session=mock_session, get_product_service=mock_get_product_service
    )

    result = await service.exec(1)

    assert product.is_active is False
    assert result == {"message": "Product removed successfully"}
    mock_session.commit.assert_awaited_once()


# ---------------------------------------------------------
# DeleteProductImageService
# ---------------------------------------------------------


@pytest.mark.asyncio
async def test_delete_product_image_success(
    mock_session,
    mock_get_product_service,
    mock_get_image_service,
    mock_delete_image_service,
):
    user = FakeUser(id=10)
    product = FakeProduct(id=1, seller_id=10)

    img1 = FakeImage(id=1, product_id=1, is_main=True)
    img2 = FakeImage(id=2, product_id=1, is_main=False)
    product.images = [img1, img2]

    mock_get_product_service.exec.return_value = product
    mock_get_image_service.exec.return_value = img1

    service = DeleteProductImageService(
        user=user,
        session=mock_session,
        get_product_service=mock_get_product_service,
        get_image_service=mock_get_image_service,
        delete_image_service=mock_delete_image_service,
    )

    updated = await service.exec(1, 1)

    assert updated.images[1].is_main is True
    mock_delete_image_service.exec.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_product_image_wrong_product(
    mock_session,
    mock_get_product_service,
    mock_get_image_service,
    mock_delete_image_service,
):
    user = FakeUser(id=10)
    product = FakeProduct(id=1, seller_id=10)
    wrong_image = FakeImage(id=5, product_id=99)

    mock_get_product_service.exec.return_value = product
    mock_get_image_service.exec.return_value = wrong_image

    service = DeleteProductImageService(
        user=user,
        session=mock_session,
        get_product_service=mock_get_product_service,
        get_image_service=mock_get_image_service,
        delete_image_service=mock_delete_image_service,
    )

    with pytest.raises(ImageNotBelongToProductException):
        await service.exec(1, 5)
