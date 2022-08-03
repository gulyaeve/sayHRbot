
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from logging import log, INFO

# from filters import AuthCheck
from loader import dp
from utils.utilities import get_bot_info


@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    help_message = """
    <b>Команды чат-бота:</b>\n
    <b>/say_thanks</b> - отправить коллеге <b>Спасибо</b>\n
    <b>/start</b> - Начало взаимодействия с ботом;\n
    <b>/auth</b> - авторизация в системе, необходима для получения доступа к возможностям бота;\n
    <b>/cancel</b> - отмена любого текущего действия;\n
    """
    # tricky_stiker = await db.select_stiker(emoji="tricky")
    # await message.answer_sticker(tricky_stiker['code'])
    await message.answer(help_message)


# @dp.message_handler(commands=['menu'])
# async def help_command(message: types.Message):
#     help_message = """
#     <b>/say_thanks</b> - отправить коллеге <b>Спасибо</b>\n
#     """
#     # tricky_stiker = await db.select_stiker(emoji="tricky")
#     # await message.answer_sticker(tricky_stiker['code'])
#     await message.answer(help_message)


# @dp.message_handler(AuthCheck(), commands=['start'])
# async def cmd_start_user(message: types.Message):
#     """
#     Conversation's entry point
#     """
#     log(INFO, f"[{message.from_user.id=}] with auth нажал START.")
#     me = await get_bot_info()
#     await message.reply(f"Добро пожаловать в чат-бот «{me.full_name}»! 😁")
#     await message.answer("Здесь ты можешь создать открытку, для этого нажми команду <b>/say_thanks</b>")


@dp.message_handler(commands=['start'])
async def cmd_start_user(message: types.Message):
    """
    Conversation's entry point
    """
    log(INFO, f"[{message.from_user.id=}] without auth нажал START.")
    me = await get_bot_info()
    await message.reply(f"Добро пожаловать в чат-бот «{me.full_name}»! 😁")
    await message.answer("Чтобы начать работу, пройди авторизацию, для этого нажми команду: <b>/auth</b>")


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
    # sad_sticker = await db.select_stiker(emoji="sad")
    # await message.answer_sticker(sad_sticker['code'])
    await message.reply('Действие отменено.', reply_markup=types.ReplyKeyboardRemove())
