from src.config import S3_SETTINGS
from src.s3_storage.storage import S3Client

async def get_s3_client() -> S3Client:
    return S3Client(**S3_SETTINGS)
