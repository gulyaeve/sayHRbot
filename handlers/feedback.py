
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text, Regexp
from logging import log, INFO

from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import managers_chats
from loader import dp, bot
from utils.utilities import make_keyboard_list


class FeedBack(StatesGroup):
    Text = State()
    Name = State()
    InputName = State()
    # TextAndAnon = State()
    # TextAndName = State()


@dp.message_handler(commands=['feedback'])
async def feedback_command(message: types.Message):
    await message.answer("Нам важно, чтобы взаимодействие между сотрудниками в команде было легким, комфортным и "
                         "интересным, поэтому просим рассказать, что тебя тревожит, "
                         "и как мы можем помочь в данной ситуации.\n\n"
                         "🥷<i>Ты можешь сделать это анонимно или представиться (тогда у нас будет возможность обсудить "
                         "с тобой детали).</i>\n\n"
                         "✍️<b>Напиши свою обратную связь:</b>")
    log(INFO, f"{message.from_user.id=} tap to feedback")
    await FeedBack.Text.set()


@dp.message_handler(content_types=types.ContentType.TEXT, state=FeedBack.Text)
async def save_text_anon(message: types.Message, state: FSMContext):
    keyboard = make_keyboard_list([
        "Отправить анонимно",
        "Представиться"
    ])
    async with state.proxy() as data:
        data['feedback'] = message.text
    await message.answer("Представишься или отправить анонимно?", reply_markup=keyboard)
    await FeedBack.Name.set()


@dp.message_handler(Text(equals="Отправить анонимно"), content_types=types.ContentType.TEXT, state=FeedBack.Name)
async def choose_name_anon(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await message.answer("Спасибо, что делишься с нами обратной связью!",
                         reply_markup=types.ReplyKeyboardRemove())
    inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="Ответить на этот фидбек",
                             callback_data=f'reply_for_feedback={message.from_user.id}')]])
    for manager in managers_chats:
        await bot.send_message(manager,
                               f"#feedback\n"
                               f"<i>Аноним</i> написал ФИБДЕК:\n"
                               f"<code>{data['feedback']}</code>",
                               reply_markup=inline_keyboard)
    await state.finish()


@dp.message_handler(Text(equals="Представиться"), content_types=types.ContentType.TEXT, state=FeedBack.Name)
async def choose_name(message: types.Message, state: FSMContext):
    await message.answer("Введи ФИО:", reply_markup=types.ReplyKeyboardRemove())
    await FeedBack.InputName.set()


@dp.message_handler(content_types=types.ContentType.ANY, state=FeedBack.Name)
async def no_choose(message: types.Message):
    return await message.answer("Выбери вариант на клавиатуре:")


@dp.message_handler(content_types=types.ContentType.TEXT, state=FeedBack.InputName)
async def save_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    # data = await state.get_data()
    await message.answer("Спасибо, что делишься с нами обратной связью!",
                         reply_markup=types.ReplyKeyboardRemove())
    inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="Ответить на этот фидбек",
                             callback_data=f'reply_for_feedback={message.from_user.id}')]])
    for manager in managers_chats:
        await bot.send_message(manager,
                               f"#feedback\n"
                               f"<i>{data['name']}</i> написал ФИБДЕК:\n"
                               f"<code>{data['feedback']}</code>",
                               reply_markup=inline_keyboard)
    await state.finish()
#
#
# @dp.message_handler(content_types=types.ContentType.TEXT, state=FeedBack.TextAndName)
# async def save_text_anon(message: types.Message, state: FSMContext):
#     async with state.proxy() as data:
#         data['feedback'] = message.text
#     await message.answer("Спасибо, что делишься с нами обратной связью!")
#     inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[[
#         InlineKeyboardButton(text="Ответить на этот фидбек",
#                              callback_data=f'reply_for_feedback={message.from_user.id}')]])
#     for manager in managers_chats:
#         await bot.send_message(manager,
#                                f"#feedback\n"
#                                f"<i>{data['name']}</i> написал ФИБДЕК:\n"
#                                f"<code>{data['feedback']}</code>",
#                                reply_markup=inline_keyboard)
#     await state.finish()


@dp.callback_query_handler(Regexp('reply_for_feedback=([0-9]*)'))
async def answer_to_text(callback: types.CallbackQuery, state: FSMContext):
    reply_user_id = callback.data.split("=")[1]
    log(INFO, f"В {callback.message.chat.id=} готовится ответ для {reply_user_id=}")
    async with state.proxy() as data:
        data["feedback_user_id"] = reply_user_id
        data["message_id"] = callback.message.message_id
    await callback.message.answer(f"Введите ответ (только текст):")
    await state.set_state("ANSWER_TO_FEEDBACK")


@dp.message_handler(state="ANSWER_TO_FEEDBACK", content_types=types.ContentType.ANY)
async def send_answer_to_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    log(INFO, f"Из {message.chat.id=} отправлен ответ {data['feedback_user_id']=}")
    # await bot.copy_message(data['feedback_user_id'], message.chat.id, message.message_id)
    await bot.send_message(data['feedback_user_id'], f"Ответ от команды HR на твой фидбек:")
    await bot.copy_message(data['feedback_user_id'], message.chat.id, message.message_id)
    await bot.edit_message_reply_markup(message.chat.id, data['message_id'], reply_markup=None)
    await message.answer("Ответ отправлен")
    log(INFO, f'Пользователю [{data["feedback_user_id"]=}] отправлено: {message.message_id}')
    await state.finish()
