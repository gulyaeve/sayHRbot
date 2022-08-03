
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from logging import log, INFO

from loader import dp
from utils.utilities import get_bot_info


@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    help_message = """
    <b>Команды чат-бота:</b>\n
    <b>/start</b> - Начать работу с ботом;\n
    <b>/help</b> - Помощь по командам чат-бота;\n
    <b>/question</b> - Задать вопрос;\n
    <b>/feedback</b> - Оставить обратную связь;\n
    <b>/idea</b> - Предложить идею;\n
    <b>/cancel</b> - отмена любого текущего действия;\n
    """
    await message.answer(help_message)


@dp.message_handler(commands=['start'])
async def cmd_start_user(message: types.Message):
    """
    Conversation's entry point
    """
    log(INFO, f"[{message.from_user.id=}] without auth нажал START.")
    me = await get_bot_info()
    await message.reply(f"Добро пожаловать в чат-бот «{me.full_name}»!")
    await message.answer("Нажми <b>/help</b>, чтобы узнать какие есть команды в чат-боте")


# You can use state '*' if you need to handle all states
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
@dp.message_handler(Text(equals='отмена', ignore_case=True), state='*')
@dp.message_handler(state='*', commands=['cancel'])
async def cancel_handler(message: types.Message, state: FSMContext):
    """
    Allow user to cancel any action
    """
    log(INFO, f"[{message.from_user.id=}] отменил действие.")
    await state.finish()
    await message.reply('Действие отменено.', reply_markup=types.ReplyKeyboardRemove())
