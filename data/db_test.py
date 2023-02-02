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

    orders_loading = await OrdersLoading.query.where(OrdersLoading.order_end == None).gino.all()
    res_orders = [i for i in orders_loading if 5761065854 in i.persons_list]
    for i in res_orders:
        print(i.persons_list)

loop = asyncio.get_event_loop()
loop.run_until_complete(db_test())
