import base64
import hashlib
import hmac
import re
import struct
from datetime import datetime

from aiogram import Bot, Dispatcher

from src.config import BOT_TOKEN


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


def encode_record_id(record_id: int, secret_key: bytes) -> str:
    """
    Кодирование ID с HMAC для проверки целостности
    """
    id_bytes = struct.pack('>Q', record_id)
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

        record_id = struct.unpack('>Q', id_bytes)[0]

        return record_id

    except Exception as e:
        raise ValueError(f"Неверный hash: {str(e)}")


def parse_order_string(s: str) -> dict:
    s = s.strip().strip("{}")
    pairs = [p.strip() for p in s.split(",") if p.strip()]
    result = {}
    for p in pairs:
        key, value = map(str.strip, p.split(":", 1))
        if value.lower() in ("true", "false"):
            result[key] = value.lower() == "true"
        elif re.fullmatch(r"\d+", value):
            result[key] = int(value)
        elif re.fullmatch(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+", value):
            result[key] = datetime.strptime(value, "%Y-%m-%d %H:%M:%S.%f")
        else:
            result[key] = value
    return result


def escape_markdown_v2(text):
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return ''.join(['\\' + char if char in escape_chars else char for char in text])