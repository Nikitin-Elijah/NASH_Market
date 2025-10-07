import asyncio

from utils import bot, dp
from handlers import routers


async def main() -> None:
    """
    Основная функция для инициализации и запуска работы бота
    """
    for router in routers:
        dp.include_router(router)

    try:
        bot_info = await bot.get_me()
        print(f'Bot @{bot_info.username} has started.')

        await dp.start_polling(bot)

    except Exception as e:
        print(e)

    finally:
        await bot.close()


if __name__ == '__main__':
    asyncio.run(main())
