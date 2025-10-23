import json
from aiogram import Router, types, F
from aiogram.filters import Command
from data.quiz_data import quiz_data
from keyboards.builders import generate_options_keyboard, get_main_menu_keyboard, get_thanks_keyboard
from database import update_quiz_state, get_quiz_state, save_user_stats

router = Router()


async def new_quiz(message: types.Message):
    user_id = message.from_user.id
    await update_quiz_state(user_id, 0, json.dumps([]))
    await get_question(message, user_id)


async def finish_quiz(message: types.Message, user_id: int, answers: list):
    # Подсчет результатов по темам
    scores = {'programming': 0, 'animals': 0, 'tech': 0}
    topic_questions_count = {'programming': 0, 'animals': 0, 'tech': 0}

    # Считаем количество вопросов по каждой теме
    for question in quiz_data:
        topic_questions_count[question['topic']] += 1

    # Считаем правильные ответы по темам
    for i, is_correct in enumerate(answers):
        if i < len(quiz_data):
            topic = quiz_data[i]['topic']
            if is_correct:
                scores[topic] += 1

    total_score = sum(scores.values())

    # Сохранение статистики
    user_data = {
        'user_id': user_id,
        'username': message.from_user.username or message.from_user.first_name,
        'total_score': total_score
    }
    await save_user_stats(user_data)

    # Определение рекомендуемых тем (только те, где максимальный результат)
    max_score = max(scores.values())
    recommended_topics = []

    # Добавляем только темы с максимальным счетом
    for topic, score in scores.items():
        if score == max_score:
            recommended_topics.append(topic)

    # Формирование сообщения с результатами
    result_message = (
        f"<b>Квиз завершен!</b>\n\n"
        f"Ваши результаты:\n"
        f"• Программирование: {scores['programming']}/{topic_questions_count['programming']}\n"
        f"• Животные: {scores['animals']}/{topic_questions_count['animals']}\n"
        f"• Технологии: {scores['tech']}/{topic_questions_count['tech']}\n"
        f"• Общий счет: {total_score}/{len(quiz_data)}\n\n"
    )

    # Формирование приглашений с датами
    dates = ["29 октября 2025", "30 октября 2025", "31 октября 2025"]
    topic_names = {
        'programming': 'Программирование',
        'animals': 'Все о животных',
        'tech': 'Новые технологии'
    }

    if recommended_topics:
        result_message += "Приглашаем вас на квизы:\n"
        for i, topic in enumerate(recommended_topics):
            if i < len(dates):
                result_message += f"• {topic_names[topic]} - {dates[i]}\n"

    result_message += "\nВыберите удобную дату и тему для участия!"

    await message.answer(result_message,
                        reply_markup=get_main_menu_keyboard(),
                        parse_mode="HTML")
    await message.answer("Хотите поблагодарить автора?",
                        reply_markup=get_thanks_keyboard())


async def get_question(message: types.Message, user_id: int):
    question_index, answers_json = await get_quiz_state(user_id)

    if question_index >= len(quiz_data):
        await finish_quiz(message, user_id, json.loads(answers_json))
        return

    current_question = quiz_data[question_index]
    correct_index = current_question['correct_option']
    opts = current_question['options']

    kb = generate_options_keyboard(opts, opts[correct_index])
    await message.answer(
        f"<b>Вопрос {question_index + 1}/{len(quiz_data)}:</b>\n"
        f"{current_question['question']}",
        reply_markup=kb,
        parse_mode="HTML"
    )


async def process_answer(callback: types.CallbackQuery, is_correct: bool):
    user_id = callback.from_user.id
    question_index, answers_json = await get_quiz_state(user_id)

    # Убираем кнопки
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )

    # Обновляем ответы
    answers = json.loads(answers_json)
    answers.append(is_correct)

    # Отправляем сообщение о правильности ответа с цветным текстом
    if is_correct:
        await callback.message.answer("<b>Верно!</b>", parse_mode="HTML")
    else:
        correct_option = quiz_data[question_index]['options'][quiz_data[question_index]['correct_option']]
        await callback.message.answer(
            f"<b>Неправильно!</b> Правильный ответ:<span class='tg-spoiler'> {correct_option}</span>",
            parse_mode="HTML"
        )

    # Переход к следующему вопросу
    question_index += 1
    await update_quiz_state(user_id, question_index, json.dumps(answers))
    await get_question(callback.message, user_id)


@router.callback_query(F.data == "right_answer")
async def right_answer(callback: types.CallbackQuery):
    await process_answer(callback, True)


@router.callback_query(F.data == "wrong_answer")
async def wrong_answer(callback: types.CallbackQuery):
    await process_answer(callback, False)


@router.callback_query(F.data == "thanks_author")
async def thanks_author(callback: types.CallbackQuery):
    await callback.message.answer("Спасибо, ты классный держи пивка 🍺, а если ты классная держи цветочки 💐! 😊")


@router.message(F.text == "Я самый умный")
@router.message(Command("quiz"))
async def cmd_quiz(message: types.Message):
    await message.answer("Отлично! Начинаем квиз. Удачи!", reply_markup=None)
    await new_quiz(message)


@router.message(F.text == "Остановись шайтан машина")
async def stop_quiz(message: types.Message):
    await message.answer("Квиз остановлен. Нажми 'Я самый умный' .... быстро нажми",
                         reply_markup=get_main_menu_keyboard())