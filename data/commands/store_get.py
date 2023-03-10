import logging

from sqlalchemy import and_

from data.models.store import Store
from data.models.orders import Orders, OrdersStatus, OrdersLoading
from data.models.performers import PerformerPersonalData

logger = logging.getLogger("bot.data.commands.store_get_db")

"""Функции взятия информации из БД для Магазинов"""


async def store_select(user_id):
    store = await Store.query.where(Store.user_id == user_id).gino.first()
    return store
