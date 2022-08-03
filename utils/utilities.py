import re
from logging import log, INFO

from aiogram import types

from config import bot_admins, managers_chats
from loader import bot


async def set_default_commands():
    """
    Установка команд для бота (кнопка "Меню")
    """
    return await bot.set_my_commands([
        types.BotCommand(command="/start", description="Начать работу с чат-ботом"),
        types.BotCommand(command="/help", description="Помощь по командам чат-бота"),
        types.BotCommand(command="/question", description="Задать вопрос"),
        types.BotCommand(command="/feedback", description="Оставить обратную связь"),
        types.BotCommand(command="/idea", description="Предложить идею"),
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


# async def copy_to_managers(message):
#     for manager in managers_chats:
#         try:
#             await bot.send_message(manager, message)
#         except:
#             log(INFO, f"Manager [{manager}] block this bot")


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
