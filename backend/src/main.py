import asyncio
from datetime import datetime

from celery import Celery
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import REDIS_URL, database_configuration
from src.routers import users, products, verification_code
from src.user_cleanup_service.user_cleanup_service import UserCleanupService

app = FastAPI(description='NASH market API', version='0.1.0')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(users.router)
app.include_router(products.router)
app.include_router(verification_code.router)


celery_app = Celery(
    'user_cleanup',
    broker=REDIS_URL,
    backend=REDIS_URL
)

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

@celery_app.task(name='cleanup_unverified_users_task')
def cleanup_unverified_users_task(hours_threshold: int = 24):
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
        "timestamp": datetime.utcnow().isoformat()
    }


celery_app.conf.beat_schedule = {
    'cleanup-unverified-users-every-6-hours': {
        'task': 'cleanup_unverified_users_task',
        'schedule': 21600,
        'args': [24]
    },
}


@app.get('/')
async def root() -> dict:
    return {'message': 'NASH market API root'}