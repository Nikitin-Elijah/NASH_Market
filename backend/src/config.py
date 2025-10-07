import os
from dotenv import load_dotenv

from src.database.database_config import DatabaseConfig
from src.s3_storage.storage import S3Client

load_dotenv()


# _______________DATABASE CONFIGURATION_______________
DATABASE = os.getenv('DATABASE', 'default_db')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_USER = os.getenv('DB_USER', 'user')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')
DB_PORT = os.getenv('DB_PORT', '5432')

DATABASE_URL = f'postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DATABASE}'

database_configuration: DatabaseConfig = DatabaseConfig(database_url=DATABASE_URL)


# _______________S3_STORAGE CONFIGURATION_______________
S3_ACCESS_KEY = os.getenv('S3_ACCESS_KEY')
S3_SECRET_KEY = os.getenv('S3_SECRET_KEY')
ENDPOINT_URL = os.getenv('ENDPOINT_URL')
BUCKET_NAME = os.getenv('BUCKET_NAME')
STORAGE_URL = os.getenv('STORAGE_URL')

STORAGE_INFO = {
    'access_key': S3_ACCESS_KEY,
    'secret_key': S3_SECRET_KEY,
    'endpoint_url': ENDPOINT_URL,
    'bucket_name': BUCKET_NAME
}

s3_storage: S3Client = S3Client(**STORAGE_INFO)


# _______________AUTH CONFIGURATION_______________
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = "HS256"

# _______________VERIFICATION CONFIGURATION_______________
VERIFICATION_SECRET_KEY = os.getenv('VERIFICATION_SECRET_KEY')

# _______________REDIS CONFIGURATION_______________
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = os.getenv('REDIS_PORT', '6379')
REDIS_DB = os.getenv('REDIS_DB', 'default_db')

REDIS_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'