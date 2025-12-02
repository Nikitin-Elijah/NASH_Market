import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import UploadFile
from io import BytesIO

# ------------------------------
# Fake Models (имитация ORM моделей)
# ------------------------------


class FakeUser:
    def __init__(
        self,
        id: int = 1,
        username: str = "testuser",
        is_active: bool = False,
        received_reviews: list = None,
    ):
        self.id = id
        self.username = username
        self.hashed_password = "hashed"
        self.is_active = is_active
        self.tg_user_id = None
        self.tg_username = None
        self.verified_at = None
        self.received_reviews = received_reviews


class FakeProduct:
    def __init__(self, id=1, seller_id=10, is_active=True):
        self.id = id
        self.seller_id = seller_id
        self.is_active = is_active
        self.images = []


class FakeImage:
    def __init__(
        self, id=1, product_id=1, is_main=False, url="https://fake.storage/file.png"
    ):
        self.id = id
        self.product_id = product_id
        self.is_main = is_main
        self.url = url


class FakeProductForPurchase:
    def __init__(self, id=1, seller_id=10):
        self.id = id
        self.seller_id = seller_id


class FakePurchase:
    def __init__(
        self,
        id=1,
        product_id=1,
        seller_id=10,
        buyer_id=1,
        comment="test comment",
        permission=False,
        refusal=False,
        successful=True,
    ):
        self.id = id
        self.product_id = product_id
        self.seller_id = seller_id
        self.buyer_id = buyer_id
        self.comment = comment
        self.permission = permission
        self.refusal = refusal
        self.successful = successful


class FakeVerificationCode:
    def __init__(
        self,
        id=1,
        user_id=1,
        code=123456,
        activate=False,
        tg_user_id=1001,
        tg_username="tg_test",
    ):
        self.id = id
        self.user_id = user_id
        self.code = code
        self.activate = activate
        self.tg_user_id = tg_user_id
        self.tg_username = tg_username


class FakeReview:
    def __init__(
        self, id: int, author_id: int, recipient_id: int, text: str, rating: int
    ):
        self.id = id
        self.author_id = author_id
        self.recipient_id = recipient_id
        self.text = text
        self.rating = rating


# ------------------------------
# Fake UploadFile
# ------------------------------


@pytest.fixture
def fake_upload_file():
    """Создаёт простой UploadFile, который можно передавать в сервисы."""
    file = UploadFile(filename="test.png", file=BytesIO(b"fake image data"))
    return file


# ------------------------------
# Mock AsyncSession
# ------------------------------


@pytest.fixture
def mock_session():
    """Мокаем AsyncSession целиком."""
    session = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.delete = AsyncMock()
    session.scalar = AsyncMock()
    return session


# ------------------------------
# Mock S3Client
# ------------------------------


@pytest.fixture
def mock_s3():
    """Мокаем S3Client, чтобы не было настоящих запросов к S3."""
    s3 = AsyncMock()
    s3.upload_file = AsyncMock()
    s3.delete_file = AsyncMock()
    return s3


# ------------------------------
# Mock сервисов
# ------------------------------


@pytest.fixture
def mock_get_product_service():
    return AsyncMock()


@pytest.fixture
def mock_add_image_service():
    return AsyncMock()


@pytest.fixture
def mock_get_image_service():
    return AsyncMock()


@pytest.fixture
def mock_delete_image_service():
    return AsyncMock()


@pytest.fixture
def mock_get_product_service_for_purchase():
    service = AsyncMock()
    service.exec = AsyncMock()
    return service


@pytest.fixture
def mock_get_purchase_service_for_update():
    service = AsyncMock()
    service.exec = AsyncMock()
    return service


@pytest.fixture
def mock_get_user_by_name_service():
    service = AsyncMock()
    service.exec = AsyncMock()
    return service


@pytest.fixture
def mock_create_user_service():
    service = AsyncMock()
    service.exec = AsyncMock()
    return service


@pytest.fixture
def mock_get_user_service():
    service = AsyncMock()
    service.exec = AsyncMock()
    return service


@pytest.fixture
def mock_get_verification_code_service():
    service = AsyncMock()
    service.exec = AsyncMock()
    return service


@pytest.fixture
def mock_get_purchase_service():
    return AsyncMock()


@pytest.fixture
def mock_recalculate_user_rating_service():
    return AsyncMock()


@pytest.fixture
def mock_check_review_service():
    service = AsyncMock()
    service.exec = AsyncMock()
    return AsyncMock()


# ------------------------------
# Дополнительные фикстуры для моделей
# ------------------------------


@pytest.fixture
def fake_user():
    return FakeUser(id=1)


@pytest.fixture
def fake_image():
    return FakeImage()
