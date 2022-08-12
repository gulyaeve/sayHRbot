
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text, Regexp
from logging import log, INFO

from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import managers_chats
from loader import dp, bot
from utils.utilities import make_keyboard_list


class Idea(StatesGroup):
    Text = State()
    Name = State()
    InputName = State()
    # TextAndAnon = State()
    # TextAndName = State()


@dp.message_handler(commands=['idea'])
async def idea_command(message: types.Message):
    await message.answer("Мы знаем, что в нашей команде много креативных и неравнодушных людей. "
                         "Напиши свою идею, а мы будем рады помочь воплотить интересные предложения в жизнь или "
                         "переадресуем их тем, кто сделает это лучше нас.\n"
                         "Ты можешь сделать это анонимно или представиться (тогда у нас будет возможность обсудить с "
                         "тобой детали).\n"
                         "Напиши, о чем хочешь нам сообщить:")
    log(INFO, f"{message.from_user.id=} tap to idea")
    await Idea.Text.set()


@dp.message_handler(content_types=types.ContentType.TEXT, state=Idea.Text)
async def save_text_anon(message: types.Message, state: FSMContext):
    keyboard = make_keyboard_list([
        "Отправить анонимно",
        "Представиться"
    ])
    async with state.proxy() as data:
        data['idea'] = message.text
    await message.answer("Представишься или отправить анонимно?", reply_markup=keyboard)
    await Idea.Name.set()


@dp.message_handler(Text(equals="Отправить анонимно"), content_types=types.ContentType.TEXT, state=Idea.Name)
async def choose_name_anon(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await message.answer("Спасибо, что участвуешь в улучшении жизни организации!",
                         reply_markup=types.ReplyKeyboardRemove())
    inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="Ответить на эту идею",
                             callback_data=f'reply_for_idea={message.from_user.id}')]])
    for manager in managers_chats:
        await bot.send_message(manager,
                               f"#idea\n"
                               f"<i>Аноним</i> написал ИДЕЮ:\n"
                               f"<code>{data['idea']}</code>",
                               reply_markup=inline_keyboard)
    await state.finish()


@dp.message_handler(Text(equals="Представиться"), content_types=types.ContentType.TEXT, state=Idea.Name)
async def choose_name(message: types.Message, state: FSMContext):
    await message.answer("Введи ФИО:", reply_markup=types.ReplyKeyboardRemove())
    await Idea.InputName.set()


@dp.message_handler(content_types=types.ContentType.ANY, state=Idea.Name)
async def no_choose(message: types.Message):
    return await message.answer("Выбери вариант на клавиатуре:")


@dp.message_handler(content_types=types.ContentType.TEXT, state=Idea.InputName)
async def save_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    # data = await state.get_data()
    await message.answer("Спасибо, что участвуешь в улучшении жизни организации!",
                         reply_markup=types.ReplyKeyboardRemove())
    inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="Ответить на эту идею",
                             callback_data=f'reply_for_idea={message.from_user.id}')]])
    for manager in managers_chats:
        await bot.send_message(manager,
                               f"#idea\n"
                               f"<i>{data['name']}</i> написал ИДЕЮ:\n"
                               f"<code>{data['idea']}</code>",
                               reply_markup=inline_keyboard)
    await state.finish()


# @dp.message_handler(content_types=types.ContentType.TEXT, state=Idea.TextAndAnon)
# async def save_text_anon(message: types.Message, state: FSMContext):
#     async with state.proxy() as data:
#         data['idea'] = message.text
#     await message.answer("Спасибо, что участвуешь в улучшении жизни организации!")
#     inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[[
#         InlineKeyboardButton(text="Ответить на эту идею",
#                              callback_data=f'reply_for_idea={message.from_user.id}')]])
#     for manager in managers_chats:
#         await bot.send_message(manager,
#                                f"#idea\n"
#                                f"<i>Аноним</i> написал ИДЕЮ:\n"
#                                f"<code>{data['idea']}</code>",
#                                reply_markup=inline_keyboard)
#     await state.finish()


# @dp.message_handler(content_types=types.ContentType.TEXT, state=Idea.TextAndName)
# async def save_text_anon(message: types.Message, state: FSMContext):
#     async with state.proxy() as data:
#         data['idea'] = message.text
#     await message.answer("Спасибо, что участвуешь в улучшении жизни организации!")
#     inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[[
#         InlineKeyboardButton(text="Ответить на эту идею",
#                              callback_data=f'reply_for_idea={message.from_user.id}')]])
#     for manager in managers_chats:
#         await bot.send_message(manager,
#                                f"#идея\n"
#                                f"<i>{data['name']}</i> написал ИДЕЮ:\n"
#                                f"<code>{data['idea']}</code>",
#                                reply_markup=inline_keyboard)
#     await state.finish()


@dp.callback_query_handler(Regexp('reply_for_idea=([0-9]*)'))
async def answer_to_text(callback: types.CallbackQuery, state: FSMContext):
    reply_user_id = callback.data.split("=")[1]
    log(INFO, f"В {callback.message.chat.id=} готовится ответ для {reply_user_id=}")
    async with state.proxy() as data:
        data["idea_user_id"] = reply_user_id
        data["message_id"] = callback.message.message_id
    await callback.message.answer(f"Введите ответ (только текст):")
    await state.set_state("ANSWER_TO_IDEA")


@dp.message_handler(state="ANSWER_TO_IDEA", content_types=types.ContentType.ANY)
async def send_answer_to_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    log(INFO, f"Из {message.chat.id=} отправлен ответ {data['idea_user_id']=}")
    # await bot.copy_message(data['idea_user_id'], message.chat.id, message.message_id)
    await bot.send_message(data['idea_user_id'], f"Ответ от команды HR:\n\n<i>{message.text}</i>")
    await bot.edit_message_reply_markup(message.chat.id, data['message_id'], reply_markup=None)
    await message.answer("Ответ отправлен")
    log(INFO, f'Пользователю [{data["idea_user_id"]=}] отправлено: {message.message_id}')
    await state.finish()
