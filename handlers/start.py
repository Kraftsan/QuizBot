from aiogram import Router, types, F
from aiogram.filters import Command
from keyboards.builders import get_main_menu_keyboard

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    welcome_text = (
        "<b>Добро пожаловать на квиз!</b>\n"
        "Этот квиз поможет узнать, какой квиз тебе подходит.\n"
        "Если ты уверен в себе и ты готов к вопросам,\n"
        "то жми на кнопку 'Я самый умный' и погнали, узнавать как квиз поможет выбрать какой квиз...\n"
        ".... ну в общем ты понял ...."
    )
    await message.answer(welcome_text,
                        reply_markup=get_main_menu_keyboard(),
                        parse_mode="HTML")