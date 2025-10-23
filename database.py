import aiosqlite

DB_NAME = 'quiz_bot.db'

async def init_db():
    """Инициализация базы данных"""
    async with aiosqlite.connect(DB_NAME) as db:
        # Таблица для состояния
        await db.execute('''CREATE TABLE IF NOT EXISTS quiz_state (
            user_id INTEGER PRIMARY KEY, 
            question_index INTEGER,
            answers TEXT
        )''')

        # Таблица для пользователей
        await db.execute('''CREATE TABLE IF NOT EXISTS user_stats (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            total_score INTEGER DEFAULT 0,
            last_played TEXT
        )''')
        await db.commit()

async def update_quiz_state(user_id: int, question_index: int, answers: str = ""):
    """Обновление состояния"""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            'INSERT OR REPLACE INTO quiz_state (user_id, question_index, answers) VALUES (?, ?, ?)',
            (user_id, question_index, answers)
        )
        await db.commit()

async def get_quiz_state(user_id: int):
    """Получение состояния"""
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(
                'SELECT question_index, answers FROM quiz_state WHERE user_id = ?',
                (user_id,)
        ) as cursor:
            result = await cursor.fetchone()
            return result if result else (0, "")

async def save_user_stats(user_data: dict):
    """Сохранение статистики"""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''INSERT OR REPLACE INTO user_stats 
            (user_id, username, total_score, last_played) 
            VALUES (?, ?, ?, datetime('now'))''',
                         (
                             user_data['user_id'],
                             user_data['username'],
                             user_data['total_score']
                         )
                         )
        await db.commit()

async def get_user_stats(user_id: int):
    """Получение статистики"""
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(
                'SELECT * FROM user_stats WHERE user_id = ?',
                (user_id,)
        ) as cursor:
            return await cursor.fetchone()

async def get_all_stats():
    """Получение общей статистики"""
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(
                'SELECT username, total_score, last_played FROM user_stats ORDER BY total_score DESC LIMIT 10'
        ) as cursor:
            return await cursor.fetchall()