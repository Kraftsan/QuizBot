import asyncio
import logging
from aiogram import Bot, Dispatcher
from handlers import start, quiz  # убрали stats
from database import init_db

# Настройка логирования
logging.basicConfig(level=logging.INFO)

async def main():
    # Инициализация бота и диспетчера
    bot = Bot(token="API_TOKEN")
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