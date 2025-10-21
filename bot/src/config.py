import os
from dotenv import load_dotenv

from database.database_config import DatabaseConfig

load_dotenv()


# _______________TELEGRAM BOT CONFIGURATION_______________
BOT_TOKEN = os.getenv('BOT_TOKEN')

# _______________DATABASE CONFIGURATION_______________
DATABASE = os.getenv('DATABASE', 'default_db')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_USER = os.getenv('DB_USER', 'user')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')
DB_PORT = os.getenv('DB_PORT', '5432')

DATABASE_URL = f'postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DATABASE}'

database_configuration: DatabaseConfig = DatabaseConfig(database_url=DATABASE_URL)

# _______________VERIFICATION CONFIGURATION_______________
VERIFICATION_SECRET_KEY = os.getenv('VERIFICATION_SECRET_KEY')