import uuid

from src.config import STORAGE_URL


def generate_avatar_filename(user_id: int, original_filename: str) -> str:
    extension = original_filename.split('.')[-1]
    filename = f"avatar_{user_id}_{uuid.uuid4().hex}.{extension}"
    return filename


def generate_product_image_filename(user_id: int, product_id: int, original_filename: str) -> str:
    extension = original_filename.split('.')[-1]
    filename = f"product_{product_id}_{user_id}_{uuid.uuid4().hex}.{extension}"
    return filename


def generate_storage_url(filename: str) -> str:
    return f'{STORAGE_URL}/{filename}'