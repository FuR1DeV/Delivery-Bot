import logging

from data.models.clients import Client
from data.models.stores import StoreOrders

logger = logging.getLogger("bot.data.commands.client_set_db")

"""Функции добавления/обновления БД для Клиента"""


async def client_add(user_id, username, telephone):
    """Клиент добавляется в БД"""
    client = Client(user_id=user_id, username=username, telephone=telephone)
    await client.create()


async def client_add_order(user_id, description, image, order_id, order_create):
    logger.info(f'Клиент {user_id} добавляет заказ {order_id}')
    order = StoreOrders(client_id=user_id, description=description, image=image,
                        order_id=order_id, order_create=order_create)
    client = await Client.query.where(Client.user_id == user_id).gino.first()
    await client.update(created_orders=client.created_orders + 1).apply()
    await order.create()
