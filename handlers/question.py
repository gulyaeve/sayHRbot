
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text, Regexp
from logging import log, INFO

from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import managers_chats
from loader import dp, bot


class Question(StatesGroup):
    TextQuestion = State()
    Name = State()
    # Send = State()


@dp.message_handler(commands=['question'])
async def question_command(message: types.Message):
    await message.answer("Напиши, что тебя интересует:")
    log(INFO, f"{message.from_user.id=} tap to question")
    await Question.TextQuestion.set()


@dp.message_handler(content_types=types.ContentType.TEXT, state=Question.TextQuestion)
async def save_text(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['question'] = message.text
    await message.answer("Вопрос не может быть отправлен анонимно. "
                         "Укажи ФИО, чтобы мы могли вернуться к тебе с ответом:")
    await Question.Name.set()


@dp.message_handler(content_types=types.ContentType.ANY, state=Question.TextQuestion)
async def save_no_text(message: types.Message):
    return await message.answer("Напиши свой вопрос текстом пожалуйста:")


@dp.message_handler(content_types=types.ContentType.TEXT, state=Question.Name)
async def save_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    await message.answer("Спасибо за вопрос!\n"
                         "Мы постараемся ответить тебе как можно быстрее! "
                         "Но ответ может занять до 3-х рабочих дней, если потребуется уточнить детали.")
    inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="Ответить на этот вопрос",
                             callback_data=f'reply_for_question={message.from_user.id}')]])
    for manager in managers_chats:
        await bot.send_message(manager,
                               f"<i>{data['name']}</i> написал ВОПРОС:\n"
                               f"<code>{data['question']}</code>",
                               reply_markup=inline_keyboard)
    await state.finish()


@dp.message_handler(content_types=types.ContentType.ANY, state=Question.TextQuestion)
async def save_no_text(message: types.Message):
    return await message.answer("Напиши своё ФИО текстом пожалуйста:")


@dp.callback_query_handler(Regexp('reply_for_question=([0-9]*)'))
async def answer_to_text(callback: types.CallbackQuery, state: FSMContext):
    reply_user_id = callback.data.split("=")[1]
    log(INFO, f"{callback.message.chat.id=} {reply_user_id=}")
    async with state.proxy() as data:
        data["question_user_id"] = reply_user_id
        data["message_id"] = callback.message.message_id
    await callback.message.answer(f"Введите ответ:")
    await state.set_state("ANSWER_TO_QUESTION")


@dp.message_handler(state="ANSWER_TO_QUESTION", content_types=types.ContentType.ANY)
async def send_answer_to_text(message: types.Message, state: FSMContext):
    log(INFO, f"{message.chat.id=} {message.from_id=} {message.message_id=}")
    data = await state.get_data()
    log(INFO, f"{message.chat.id=} {data['question_user_id']=} {message.from_id=} {message.message_id=}")
    await bot.copy_message(data['question_user_id'], message.chat.id, message.message_id)
    await bot.edit_message_reply_markup(message.chat.id, data['message_id'], reply_markup=None)
    await message.answer("Ответ отправлен")
    log(INFO, f'Пользователю [{data["question_user_id"]=}] отправлено: {message.message_id}')
    await state.finish()
