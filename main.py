import logging

import dotenv
from aiogram import Bot, Dispatcher
import asyncio
import os
from dotenv import *
from app.handlers import router
from app.datebase.models import async_main


# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

dotenv.load_dotenv()
API=os.getenv('BOT_TOKEN')

async def main():
    logger.info("Инициализация базы данных")
    await async_main()


    bot = Bot(token=API)
    dp = Dispatcher()

    dp.include_router(router)  # Добавляем роутер с обработчиками

    logger.info("Запуск бота")
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('Бот выключен')
