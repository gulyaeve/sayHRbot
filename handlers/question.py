
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text, Regexp
from logging import log, INFO

from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import managers_chats
from loader import dp, bot
from utils.utilities import make_keyboard_list


class Question(StatesGroup):
    TextQuestion = State()
    Name = State()
    InputName = State()


@dp.message_handler(commands=['question'])
async def question_command(message: types.Message):
    await message.answer("Напиши свой вопрос:")
    log(INFO, f"{message.from_user.id=} tap to question")
    await Question.TextQuestion.set()


@dp.message_handler(content_types=types.ContentType.TEXT, state=Question.TextQuestion)
async def save_text(message: types.Message, state: FSMContext):
    keyboard = make_keyboard_list([
        "Отправить анонимно",
        "Представиться"
    ])
    async with state.proxy() as data:
        data['question'] = message.text
    await message.answer("Представишься или отправить анонимно?", reply_markup=keyboard)
    await Question.Name.set()


@dp.message_handler(Text(equals="Отправить анонимно"), content_types=types.ContentType.TEXT, state=Question.Name)
async def choose_name_anon(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await message.answer("Спасибо за вопрос!\n"
                         "Мы постараемся ответить тебе как можно быстрее! "
                         "Но ответ может занять до 3-х рабочих дней, если потребуется уточнить детали.",
                         reply_markup=types.ReplyKeyboardRemove())
    inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="Ответить на этот вопрос",
                             callback_data=f'reply_for_question={message.from_user.id}')]])
    for manager in managers_chats:
        await bot.send_message(manager,
                               f"#question\n"
                               f"<i>Аноним</i> написал ВОПРОС:\n"
                               f"<code>{data['question']}</code>",
                               reply_markup=inline_keyboard)
    await state.finish()


@dp.message_handler(Text(equals="Представиться"), content_types=types.ContentType.TEXT, state=Question.Name)
async def choose_name(message: types.Message, state: FSMContext):
    await message.answer("Введи ФИО:", reply_markup=types.ReplyKeyboardRemove())
    await Question.InputName.set()


@dp.message_handler(content_types=types.ContentType.ANY, state=Question.TextQuestion)
async def save_no_text(message: types.Message):
    return await message.answer("Напиши свой вопрос текстом пожалуйста:")


@dp.message_handler(content_types=types.ContentType.TEXT, state=Question.InputName)
async def save_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    await message.answer("Спасибо за вопрос!\n"
                         "Мы постараемся ответить тебе как можно быстрее! "
                         "Но ответ может занять до 3-х рабочих дней, если потребуется уточнить детали.",
                         reply_markup=types.ReplyKeyboardRemove())
    inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="Ответить на этот вопрос",
                             callback_data=f'reply_for_question={message.from_user.id}')]])
    for manager in managers_chats:
        await bot.send_message(manager,
                               f"#question\n"
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
    log(INFO, f"В {callback.message.chat.id=} готовится ответ для {reply_user_id=}")
    async with state.proxy() as data:
        data["question_user_id"] = reply_user_id
        data["message_id"] = callback.message.message_id
    await callback.message.answer(f"Введите ответ:")
    await state.set_state("ANSWER_TO_QUESTION")


@dp.message_handler(state="ANSWER_TO_QUESTION", content_types=types.ContentType.ANY)
async def send_answer_to_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    log(INFO, f"Из {message.chat.id=} отправлен ответ {data['question_user_id']=}")
    await bot.send_message(data['question_user_id'], f"Ответ от команды HR на твой вопрос:")
    await bot.copy_message(data['question_user_id'], message.chat.id, message.message_id)
    # await bot.send_message(data['question_user_id'], f"Ответ от команды HR:\n\n<i>{message.text}</i>")
    # await bot.edit_message_reply_markup(message.chat.id, data['message_id'], reply_markup=None)
    await message.answer("Ответ отправлен")
    log(INFO, f'Пользователю [{data["question_user_id"]=}] отправлено: {message.message_id}')
    await state.finish()
