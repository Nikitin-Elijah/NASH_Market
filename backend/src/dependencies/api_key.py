from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

from src.config import BOT_API_KEY

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def validate_api_key(api_key: str = Security(api_key_header)):
    if api_key != BOT_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key"
        )
    return api_key