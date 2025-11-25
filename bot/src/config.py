import os
from dotenv import load_dotenv


load_dotenv()


# _______________TELEGRAM BOT CONFIGURATION_______________
BOT_TOKEN = os.getenv("BOT_TOKEN")

# _______________VERIFICATION CONFIGURATION_______________
VERIFICATION_SECRET_KEY = os.getenv("VERIFICATION_SECRET_KEY")

# _______________RABBITMQ CONFIGURATION_______________
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "guest")
RABBITMQ_PORT = os.getenv("RABBITMQ_PORT", "5672")

RABBITMQ_URL = (
    f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@{RABBITMQ_HOST}:{RABBITMQ_PORT}/"
)

# _______________API CONFIGURATION_______________
API_BASE_URL = os.getenv("API_BASE_URL")
BOT_API_KEY = os.getenv("BOT_API_KEY")