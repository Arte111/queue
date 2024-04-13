from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, \
    ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

import text

""" Admin """


class AdminQueueListCallBack(CallbackData, prefix="admin_queue_list"):
    queue_id: int


def admin_queue_list(user_id: int):
    from handlers import db
    user_keyboad = InlineKeyboardBuilder()

    queues = db.admin_queues(user_id)
    for id in queues:
        user_keyboad.add(
            InlineKeyboardButton(text=f"{db.queue_name(id)} ({id}) : {db.user_count(id)}", callback_data=AdminQueueListCallBack(queue_id=id).pack()))
        # TODO: допилить количество участников в очереди в качестве кнопки без callback справа

    user_keyboad.add(InlineKeyboardButton(text="Создать очередь", callback_data="create_queue"))
    user_keyboad.adjust(1)  # TODO: add info with number of users in queue and resie kb
    return user_keyboad.as_markup()


class AdminQueueSettingsCallBack(CallbackData, prefix="admin_queue_settings"):
    move: str | None = None
    queue_id: int


def admin_queue(queue_id: int):
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text="Пригласить следующего",
                                callback_data=AdminQueueSettingsCallBack(move="next", queue_id=queue_id).pack()))
    kb.add(InlineKeyboardButton(text="Удалить",
                                callback_data=AdminQueueSettingsCallBack(move="delete", queue_id=queue_id).pack()))
    kb.add(InlineKeyboardButton(text="Назад", callback_data="admin_back"))
    kb.adjust(1, 2)
    return kb.as_markup()


""" User """


class UserQueueListCallBack(CallbackData, prefix="user_queue_list"):
    queue_id: int


def user_queue_list(user_id: int):
    from handlers import db
    user_keyboad = InlineKeyboardBuilder()

    queues = db.user_queues(user_id)
    for id in queues:
        user_keyboad.button(text=f"{db.queue_name(id)} ({db.place_in_queue(user_id, id)})",
                            callback_data=UserQueueListCallBack(queue_id=id))

    user_keyboad.button(text=text.join, callback_data="join")
    user_keyboad.adjust(1)
    return user_keyboad.as_markup()


class UserQueueSettingsCallBack(CallbackData, prefix="user_queue_settings"):
    queue_id: int


def user_queue(queue_id: int):
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text="Покинуть очередь",
                                callback_data=AdminQueueSettingsCallBack(queue_id=queue_id).pack()))
    kb.add(InlineKeyboardButton(text="Назад", callback_data="user_back"))
    # TODO: resize keyboard
    return kb.as_markup()
