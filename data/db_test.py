import asyncio
from datetime import datetime

from sqlalchemy import and_

from data.commands import customers_get
from data.models.admins import Payment
from data.models.customers import Customers
from data.models.orders import Orders
from settings import config
from data.db_gino import db


async def db_test():
    pass
    await db.set_bind(config.POSTGRES_URI)

    orders = await Orders.query.where(and_(Orders.user_id == 351490585,
                                           Orders.completed == 1)).gino.all()
    return print(orders)


loop = asyncio.get_event_loop()
loop.run_until_complete(db_test())
