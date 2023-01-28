import asyncio
from datetime import datetime

from sqlalchemy import and_

from data.commands import customers_get
from data.models.admins import Payment
from data.models.customers import Customers
from data.models.orders import Orders, OrdersLoading
from settings import config
from data.db_gino import db


async def db_test():
    pass
    await db.set_bind(config.POSTGRES_URI)

    order_loading = await OrdersLoading.query.where(OrdersLoading.order_id == "01_26_96697").gino.first()
    print(order_loading.persons_list)

loop = asyncio.get_event_loop()
loop.run_until_complete(db_test())
