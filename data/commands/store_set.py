import logging

from data.models.stores import Store
from data.models.orders import Orders, OrdersStatus, Reviews, OrdersLoading

logger = logging.getLogger("bot.data.commands.store_set_db")

"""Функции добавления/обновления БД для Магазина"""


async def store_add(user_id, username, telephone, store_name):
    """Магазин добавляется в БД"""
    store = Store(user_id=user_id, username=username, telephone=telephone, store_name=store_name)
    await store.create()
