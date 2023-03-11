import logging

from data.models.clients import Client
from data.models.orders import Orders, OrdersStatus, Reviews, OrdersLoading

logger = logging.getLogger("bot.data.commands.client_set_db")

"""Функции добавления/обновления БД для Клиента"""


async def client_add(user_id, username, telephone):
    """Клиент добавляется в БД"""
    client = Client(user_id=user_id, username=username, telephone=telephone)
    await client.create()
