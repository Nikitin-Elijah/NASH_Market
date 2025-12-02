import pytest
from unittest.mock import AsyncMock

from src.services.image_services import (
    GetImageService,
    AddImageService,
    DeleteImageService,
)
from src.exceptions.image_exceptions import ImageNotFoundException

# ------------------------------
# Tests for GetImageService
# ------------------------------


@pytest.mark.asyncio
async def test_get_image_success(mock_session, fake_user, fake_image):
    mock_session.scalar.return_value = fake_image
    service = GetImageService(user=fake_user, session=mock_session)
    result = await service.exec(image_id=1)
    assert result == fake_image
    mock_session.scalar.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_image_not_found(mock_session, fake_user):
    mock_session.scalar.return_value = None
    service = GetImageService(user=fake_user, session=mock_session)
    with pytest.raises(ImageNotFoundException):
        await service.exec(image_id=1)


# ------------------------------
# Tests for AddImageService
# ------------------------------


@pytest.mark.asyncio
async def test_add_image_success(mock_session, mock_s3, fake_user, fake_upload_file):
    service = AddImageService(user=fake_user, session=mock_session, storage=mock_s3)
    result = await service.exec(product_id=1, image=fake_upload_file, is_main=True)

    # Проверяем, что S3 был вызван
    mock_s3.upload_file.assert_awaited_once()
    # Проверяем, что объект добавлен в сессию
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once()
    # Проверяем, что результат имеет правильный URL
    assert hasattr(result, "url")


# ------------------------------
# Tests for DeleteImageService
# ------------------------------


@pytest.mark.asyncio
async def test_delete_image_success(mock_session, mock_s3, fake_user, fake_image):
    mock_get_image_service = AsyncMock()
    mock_get_image_service.exec.return_value = fake_image

    service = DeleteImageService(
        user=fake_user,
        session=mock_session,
        get_image_service=mock_get_image_service,
        storage=mock_s3,
    )
    result = await service.exec(image_id=1)

    # Проверяем вызовы
    mock_get_image_service.exec.assert_awaited_once_with(image_id=1)
    mock_s3.delete_file.assert_awaited_once_with(
        object_name=fake_image.url.split("/")[-1]
    )
    mock_session.delete.assert_awaited_once_with(fake_image)
    mock_session.commit.assert_awaited_once()

    assert result == {"message": "Image removed successfully"}
