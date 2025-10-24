import asyncio
import logging
from aiogram import Bot, Dispatcher
from handlers import start, quiz
from database import init_db

# Настройка логирования
logging.basicConfig(level=logging.INFO)

async def main():
    # Инициализация бота и диспетчера
    bot = Bot(token="8220978438:AAE4ZnG_OgadH_PA2PJovSj-8c3Qb2yLXuY")
    dp = Dispatcher()

    # Инициализация базы данных
    await init_db()

    # Регистрация роутеров
    dp.include_router(start.router)
    dp.include_router(quiz.router)

    # Запуск бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())