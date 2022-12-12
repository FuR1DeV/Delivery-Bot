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

    customers = await Customers.query.where(Customers.first_name.like("%po%")).gino.all()
    return print(customers)


loop = asyncio.get_event_loop()
loop.run_until_complete(db_test())
