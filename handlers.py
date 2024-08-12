from aiogram import types, F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram import flags
from aiogram.fsm.context import FSMContext
from states import User_input

import kb
import text
from db import DataBase

db = DataBase()
router = Router()


@router.message(Command("start"))
async def start_handler(msg: Message):
    await msg.answer(text.greet.format(name=msg.from_user.full_name))
    if not db.is_user_exist(msg.from_user.id):
        db.create_user(msg.from_user.id)


@router.message(Command("join"))
@router.callback_query(F.data == "join")
async def join_handler(msg: Message, state: FSMContext):
    await msg.answer(text.join)
    await state.set_state(User_input.queue_id_input)


@router.message(User_input.queue_id_input)
async def join_input_handler(msg: Message, state: FSMContext):
    queue_id = int(msg.text)
    try:
        db.join_user_to_queue(msg.from_user.id, queue_id)
    except:
        await msg.answer(text.queue_not_exist)
    await state.clear()
    await msg.answer(text.user, reply_markup=kb.user_queue_list(msg.from_user.id))


@router.message(Command("admin"))
async def admin_handler(msg: Message):
    await msg.answer(text.admin, reply_markup=kb.admin_queue_list(msg.from_user.id))


@router.callback_query(F.data == "create_queue")
async def create_queue(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer(text.enter_queue_info)
    await state.set_state(User_input.create_queue)


@router.message(User_input.create_queue)
async def create_queue_handler(msg: Message, state: FSMContext):
    db.create_queue(msg.from_user.id, str(msg.text))
    await state.clear()
    await msg.answer(text.admin, reply_markup=kb.admin_queue_list(msg.from_user.id))


@router.callback_query(kb.AdminQueueListCallBack.filter())
async def admin_queue_info(callback_query: CallbackQuery, callback_data: kb.AdminQueueListCallBack):
    await callback_query.message.edit_text(
        text.queue_info.format(name=db.queue_name(callback_data.queue_id), id=callback_data.queue_id),
        reply_markup=kb.admin_queue(callback_data.queue_id))


@router.callback_query(kb.AdminQueueSettingsCallBack.filter())
async def admin_queue_settings(callback_query: CallbackQuery, callback_data: kb.AdminQueueSettingsCallBack):
    if callback_data.move == "next":
        """ Приглашение следующего в очереди """
        from main import Bot, ParseMode
        import config
        bot = Bot(token=config.BOT_TOKEN, parse_mode=ParseMode.HTML)
        user_id = db.get_user_from_queue(callback_data.queue_id)
        await bot.send_message(user_id, f"Вас приглашают в очереди {db.queue_name(callback_data.queue_id)}")
    elif callback_data.move == "delete":
        """ Удаление очереди """
        db.remove_queue(callback_query.from_user.id, callback_data.queue_id)  # TODO: убрать user_id для передачи
        await callback_query.message.edit_text(text.queues,
                                               reply_markup=kb.admin_queue_list(callback_query.from_user.id))


@router.callback_query(F.data == "admin_back")
async def admin_back(callback_query: CallbackQuery):
    await callback_query.message.edit_text(text.queues, reply_markup=kb.admin_queue_list(callback_query.from_user.id))


@router.message(Command("user"))
async def user_handler(msg: Message):
    await msg.answer(text.user, reply_markup=kb.user_queue_list(msg.from_user.id))


@router.callback_query(kb.UserQueueListCallBack.filter())
async def user_queue_info(callback_query: CallbackQuery, callback_data: kb.UserQueueListCallBack):
    await callback_query.message.edit_text(
        text.queue_info.format(name=db.queue_name(callback_data.queue_id), id=callback_data.queue_id),
        reply_markup=kb.user_queue(callback_data.queue_id))


@router.callback_query(kb.UserQueueSettingsCallBack.filter())
async def user_queue_settings(callback_query: CallbackQuery, callback_data: kb.UserQueueSettingsCallBack):
    db.separate_queue(callback_query.from_user.id, callback_data.queue_id)
    await callback_query.message.edit_text(text.queues, reply_markup=kb.user_queue_list(callback_query.from_user.id))


@router.callback_query(F.data == "user_back")
async def user_back(callback_query: CallbackQuery):
    await callback_query.message.edit_text(text.queues, reply_markup=kb.user_queue_list(callback_query.from_user.id))
