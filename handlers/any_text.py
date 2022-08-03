from logging import log, INFO

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Regexp
from aiogram.types import ContentType, InlineKeyboardMarkup, InlineKeyboardButton

from config import bot_admins
from loader import dp, bot


@dp.message_handler(content_types=ContentType.ANY)
async def content_handler(message: types.Message):
    """
    Any content handler
    """
    log(INFO, f"[{message.from_user.id=}] отправил: {message.content_type=}")
    await message.answer("ℹ️ Для получения справки по командам чат-бота выбери команду:\n<b>/help</b>")
    inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="Ответить", callback_data=f'reply_from_anytext_id={message.from_user.id}')]])
    for bot_admin in bot_admins:
        try:
            await message.forward(bot_admin)
            await bot.send_message(bot_admin,
                                   f"[{message.from_user.full_name}; @{message.from_user.username}; {message.from_user.id}]"
                                   f" отправил: {message.content_type}", reply_markup=inline_keyboard)
        except:
            log(INFO, f"Failed to send to admin [{bot_admin}]")


@dp.callback_query_handler(Regexp('reply_from_anytext_id=([0-9]*)'))
async def answer_to_text(callback: types.CallbackQuery, state: FSMContext):
    reply_user_id = callback.data.split("=")[1]
    async with state.proxy() as data:
        data["reply_user_id"] = reply_user_id
    await callback.message.answer(f"Введите ответ:")
    await state.set_state("ANSWER_TO_ANY_TEXT")


@dp.message_handler(state="ANSWER_TO_ANY_TEXT", content_types=types.ContentType.ANY)
async def send_answer_to_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    # await message.forward(data["reply_user_id"])
    await bot.copy_message(data['reply_user_id'], message.from_id, message.message_id)
    # await bot.send_message(data["reply_user_id"], message.text)
    log(INFO, f'Пользователю [{data["reply_user_id"]=}] отправлено: {message.message_id}')
    await state.finish()
