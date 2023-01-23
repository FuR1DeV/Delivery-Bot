import logging
from datetime import datetime

import aioschedule
from aiogram import executor, types
from aiogram.dispatcher import FSMContext
import asyncio

from bot import dp, bot
from data.commands import general_set, performers_set, admins_set, admins_get, general_get
from handler_customer import register_customer
from handler_performer import register_performer
from handler_admin import register_admin_handler
from markups import markup_start, markup_admin
from settings import config
from states import states


def init_logger(name):
    logger_ = logging.getLogger(name)
    format_ = '%(asctime)s -:- %(levelname)s -:- %(name)s -:- %(message)s'
    logger_.setLevel(logging.DEBUG)
    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter(format_))
    console.setLevel(logging.DEBUG)
    info_debug = logging.FileHandler(filename="logs/info_debug.log")
    info_debug.setFormatter(logging.Formatter(format_))
    info_debug.setLevel(logging.DEBUG)
    err_warning = logging.FileHandler(filename="logs/err_warning.log")
    err_warning.setFormatter(logging.Formatter(format_))
    err_warning.setLevel(logging.WARNING)
    logger_.addHandler(console)
    logger_.addHandler(info_debug)
    logger_.addHandler(err_warning)
    logger_.debug("Логгер инициализирован")


init_logger('bot')
logger = logging.getLogger("bot.main")


@dp.message_handler(commands='start', state='*')
async def start(message: types.Message, state: FSMContext):
    await bot.send_message(message.from_user.id,
                           f'Добро пожаловать в Telegram Bot который поможет найти исполнителя '
                           f'или подзаработать', reply_markup=markup_start.markup_clean)
    await state.finish()
    await bot.send_message(message.from_user.id,
                           f'Ты заказчик или исполнитель {message.from_user.first_name} ?',
                           reply_markup=markup_start.inline_start)


@dp.message_handler(commands='admin', state='*')
async def admin(message: types.Message, state: FSMContext):
    await state.finish()
    if str(message.from_user.id) in config.ADMIN_ID:
        admin_ = await admins_get.admin_select(message.from_user.id)
        if not admin_:
            await admins_set.admin_add(message.from_user.id,
                                       message.from_user.username,
                                       message.from_user.first_name,
                                       message.from_user.last_name)
        await bot.send_message(message.from_user.id,
                               f'Добро пожаловать в панель администратора',
                               reply_markup=markup_admin.admin_main())
        await states.AdminStates.enter.set()
    else:
        await bot.send_message(message.from_user.id, "У вас нет прав доступа!")


@dp.message_handler(content_types=["new_chat_members"])
async def user_joined(message: types.Message):
    logger.debug(f'Пользователь {message.from_user.id} вошел в закрытый чат')
    await message.delete()


@dp.message_handler(content_types=["left_chat_member"])
async def user_left(message: types.Message):
    logger.debug(f'Пользователь {message.from_user.id} ВЫШЕЛ из закрытого чат')
    await message.delete()


@dp.message_handler(commands=["kick"])
async def kick_user_handler(message: types.Message):
    await bot.ban_chat_member(message.chat.id, message.from_user.id)
    await general_set.private_chat_delete_user(message.from_user.id)


@dp.message_handler()
async def bad_words(message: types.Message):
    count = 5
    lists = ["бля", "блять", "сука", "гандон", "гондон", "хуй", "пидр", "пидор", "лох", "блядь", "ебать",
             "ебля", "пизда", "блядина", "блядский", "блядство", "выблядок", "выебон", "выёбывается",
             "доебался", "ебало", "ебанёшься", "ебанул", "ебанулся", "ебашит", "ёбнул", "заебал", "заебись", "заёб",
             "ебля", "наебашился", "наебнулся", "пёзды", "пиздабол", "пиздатый", "пиздец", "поебень",
             "распиздяй", "спиздил", "уёбище", "хитровыебанный", "хуёво", "хуйня"]
    for i in lists:
        if i in message.text.lower():
            await message.delete()
            await general_set.private_chat_change_count_word(message.from_user.id)
            words = await general_get.check_private_chat_count_word(message.from_user.id)
            ban = count - words
            if ban == 0:
                await kick_user_handler(message)
            else:
                await message.answer(f"<b>У вас осталось {count - words} слова</b>\n"
                                     f"<b>Не материтесь {message.from_user.first_name} "
                                     f"иначе вы будете заблокированы!</b>")


@dp.chat_join_request_handler(state="*")
async def join_request(message: types.ChatJoinRequest):
    await performers_set.private_chat_add(message.from_user.id, 0, datetime.now().strftime('%d-%m-%Y, %H:%M:%S'))
    await bot.send_message(message.from_user.id,
                           '<b>Поздравляю вы были добавлены приватную группу доставщиков!</b>')
    await message.approve()


async def db_checker_orders_expired():
    orders = await general_get.check_orders_expired()
    for i in orders:
        limitation = str(datetime.now() - datetime.strptime(i.order_expired, '%d-%m-%Y, %H:%M:%S'))[:1]
        if limitation != "-":
            await general_set.delete_order_expired(i.order_id)


async def db_checker_orders_status():
    await general_set.check_orders_status()


async def scheduler():
    aioschedule.every().minute.do(db_checker_orders_expired)
    aioschedule.every().second.do(db_checker_orders_status)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def on_startup(_):
    asyncio.create_task(scheduler())

    from data.db_gino import db
    from data import db_gino
    print("Database connected")
    await db_gino.on_startup(dp)

    """Удалить БД"""
    # await db.gino.drop_all()

    """Создание БД"""
    await db.gino.create_all()
    await general_set.create_commission()

    """Регистрация хэндлеров"""
    register_customer(dp)
    register_performer(dp)
    register_admin_handler(dp)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
