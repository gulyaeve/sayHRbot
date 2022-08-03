import enum

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


class ManagerCallbacks(enum.Enum):
    get_staff = "get_staff"
    add_employee = "add_employee"
    get_contact_card = "get_contact_card"
    get_contact_fields = "get_contact_fields"
    remove_employee = "remove_employee"
    create_mailing = "create_mailing"


class ManagersMenu:
    manager_main_menu = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Получить список сотрудников",
                                     callback_data=ManagerCallbacks.get_staff.value)
            ],
            [
                InlineKeyboardButton(text="Добавить",
                                     callback_data=ManagerCallbacks.add_employee.value),
                InlineKeyboardButton(text="Блокировать",
                                     callback_data=ManagerCallbacks.remove_employee.value)
            ],
            [
                InlineKeyboardButton(text="Создать рассылку",
                                     callback_data=ManagerCallbacks.create_mailing.value)
            ],
        ]
    )
    manager_add_employee = InlineKeyboardMarkup(
        inline_keyboard=[
            # [
            #     InlineKeyboardButton(text="Загрузить карточку контакта",
            #                          callback_data=ManagerCallbacks.get_contact_card.value)
            # ],
            [
                InlineKeyboardButton(text="Заполнить данные вручную",
                                     callback_data=ManagerCallbacks.get_contact_fields.value)
            ]
        ]
    )
