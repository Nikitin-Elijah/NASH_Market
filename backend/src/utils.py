import random
import uuid
import base64
import hmac
import hashlib
import struct

from src.config import STORAGE_URL


def generate_avatar_filename(user_id: int, original_filename: str) -> str:
    extension = original_filename.split(".")[-1]
    filename = f"avatar_{user_id}_{uuid.uuid4().hex}.{extension}"
    return filename


def generate_product_image_filename(
    user_id: int, product_id: int, original_filename: str
) -> str:
    extension = "png"
    filename = f"product_{product_id}_{user_id}_{uuid.uuid4().hex}.{extension}"
    return filename


def generate_storage_url(filename: str) -> str:
    return f"{STORAGE_URL}/{filename}"


def encode_record_id(record_id: int, secret_key: bytes) -> str:
    """
    Кодирование ID с HMAC для проверки целостности
    """
    id_bytes = struct.pack(">Q", record_id)
    hmac_digest = hmac.new(secret_key, id_bytes, hashlib.sha256).digest()
    combined = id_bytes + hmac_digest[:8]
    encoded = base64.urlsafe_b64encode(combined).decode()

    return encoded


def decode_record_id(hash_string: str, secret_key: bytes) -> int:
    """
    Декодирование с проверкой HMAC
    """
    try:
        decoded = base64.urlsafe_b64decode(hash_string.encode())
        id_bytes = decoded[:8]
        received_hmac = decoded[8:16]
        expected_hmac = hmac.new(secret_key, id_bytes, hashlib.sha256).digest()[:8]

        if not hmac.compare_digest(received_hmac, expected_hmac):
            raise ValueError("Неверная HMAC проверка")

        record_id = struct.unpack(">Q", id_bytes)[0]

        return record_id

    except Exception as e:
        raise ValueError(f"Неверный hash: {str(e)}")


def generate_six_digit_code() -> str:
    """
    Базовая генерация 6-значного кода
    """
    return "".join([str(random.randint(1, 9)) for _ in range(6)])


def generate_invite_link(reg_hash: str) -> str:
    return f"https://t.me/nash_market_bot?start=reg_{reg_hash}"
