import re
from logging import log, INFO

from aiogram import types

from config import bot_admins
from loader import bot


async def set_default_commands():
    """
    Установка команд для бота (кнопка "Меню")
    """
    return await bot.set_my_commands([
        types.BotCommand(command="/start", description="Начать работу с чат-ботом"),
        types.BotCommand(command="/say_thanks", description="Отправить благодарность коллеге"),
        types.BotCommand(command="/help", description="Помощь по командам чат-бота"),
        types.BotCommand(command="/cancel", description="Отмена текущего действия"),
    ])


async def get_bot_info() -> types.User:
    me = await bot.get_me()
    return me


async def notify_admins(message):
    for bot_admin in bot_admins:
        try:
            await bot.send_message(bot_admin, message)
        except:
            log(INFO, f"Admin [{bot_admin}] block this bot")


# async def validate(date_text):
#     try:
#         datetime.strptime(date_text, '%Y-%m-%d')
#         return 1
#     except ValueError:
#         raise ValueError("Incorrect data format, should be YYYY-MM-DD")

# def get_key(d: dict, value):
#     for k, v in d.items():
#         if v == value:
#             return k


def make_keyboard_dict(buttons: dict):
    keyboard = types.ReplyKeyboardMarkup()
    for button in buttons.values():
        keyboard.add(button)
    keyboard.add("ОТМЕНА")
    return keyboard


def make_keyboard_list(buttons: list):
    keyboard = types.ReplyKeyboardMarkup()
    for button in buttons:
        keyboard.add(button)
    keyboard.add("ОТМЕНА")
    return keyboard


def make_text(input_text):
    return re.sub(r'<.*?>', '', input_text)
