import asyncio
from datetime import datetime

from celery import Celery
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import REDIS_URL, database_configuration, ES
from src.api.routers import products, purchases, reviews, users, verification_code
from src.midlewares.logging_midleware import LoggingMiddleware
from src.search_service.es_update_products_service import ESUpdateProductsService
from src.user_cleanup_service.user_cleanup_service import UserCleanupService

app = FastAPI(description="NASH market API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(
    LoggingMiddleware,
    log_request_body=True,
    log_response_body=True,
    max_body_size=512,
    include_traceback_in_logs=False,
    hide_sensitive_headers=["authorization"]
)

app.include_router(users.router)
app.include_router(products.router)
app.include_router(verification_code.router)
app.include_router(purchases.rabbit_router)
app.include_router(purchases.router)
app.include_router(reviews.router)


celery_app = Celery("user_cleanup", broker=REDIS_URL, backend=REDIS_URL)


loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)


@celery_app.task(name="cleanup_unverified_users_task")
def cleanup_unverified_users_task(hours_threshold: int = 1):
    """
    Фоновая задача для очистки неактивных пользователей
    """
    cleanup_service = UserCleanupService(database=database_configuration)

    async def run():
        return await cleanup_service.delete_unverified_users(hours_threshold)

    deleted_count = loop.run_until_complete(run())

    return {
        "task": "cleanup_unverified_users",
        "deleted_count": deleted_count,
        "threshold_hours": hours_threshold,
        "timestamp": datetime.now().isoformat(),
    }


@celery_app.task(name="update_products_es_task")
def update_products_es_task():
    """
    Фоновая задача для обновления товаров в ElasticSearch
    """
    es_service = ESUpdateProductsService(ES)

    async def run():
        return await es_service.update_products()

    try:
        result = loop.run_until_complete(run())
        return {
            "task": "update_products_es",
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "message": "Индекс товаров успешно обновлен",
        }

    except Exception as e:
        return {
            "task": "update_products_es",
            "status": "error",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
        }


celery_app.conf.beat_schedule = {
    "cleanup-unverified-users-every-1-hour": {
        "task": "cleanup_unverified_users_task",
        "schedule": 3600,
        "args": [1],
    },
    "update-products-es-daily": {
        "task": "update_products_es_task",
        "schedule": 3600 * 24,
        "args": [],
    },
}


@app.get("/")
async def root() -> dict:
    return {"message": "NASH market API root"}
