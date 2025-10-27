import os
from dotenv import load_dotenv
from elasticsearch import Elasticsearch

from src.database.database_config import DatabaseConfig
from src.s3_storage.storage import S3Client
from src.search_service.searcher_impl import ElasticsearchSearcher

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

# ________________AUTH CONFIGURATION_________________
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = "HS256"

# _____________VERIFICATION CONFIGURATION____________
VERIFICATION_SECRET_KEY = os.getenv('VERIFICATION_SECRET_KEY')

# ________________REDIS CONFIGURATION________________
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = os.getenv('REDIS_PORT', '6379')
REDIS_DB = os.getenv('REDIS_DB', 'default_db')

REDIS_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'

#_______________RABBITMQ CONFIGURATION_______________
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'guest')
RABBITMQ_PASSWORD = os.getenv('RABBITMQ_PASSWORD', 'guest')
RABBITMQ_PORT = os.getenv('RABBITMQ_PORT', '5672')

RABBITMQ_URL = f'amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@{RABBITMQ_HOST}:{RABBITMQ_PORT}/'

#_______________ELASTICSEARCH CONFIGURATION_______________
ELASTICSEARCH_HOST = os.getenv('ELASTICSEARCH_HOST', 'localhost')
ELASTICSEARCH_PORT = os.getenv('ELASTICSEARCH_PORT', '9200')

ELASTICSEARCH_URL = f'http://{ELASTICSEARCH_HOST}:{ELASTICSEARCH_PORT}'
ES = Elasticsearch(ELASTICSEARCH_URL)

PRODUCTS_ALIAS_NAME = 'products-current'

PRODUCTS_SEARCHER = ElasticsearchSearcher(ES, PRODUCTS_ALIAS_NAME)