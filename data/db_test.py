import asyncio
from datetime import datetime

from sqlalchemy import and_

from data.commands import customers_get, performers_get
from data.models.admins import Payment
from data.models.customers import Customers
from data.models.orders import Orders, OrdersLoading
from data.models.performers import AutoSendJobOffer
from settings import config
from data.db_gino import db


async def db_test():
    pass
    await db.set_bind(config.POSTGRES_URI)
    jobs = await performers_get.performer_select(5761065854)
    time1 = datetime.strptime(jobs.time_geo_position, '%d-%m-%Y, %H:%M:%S')
    time2 = datetime.now()
    res = time2 - time1
    print(res)
    print(f"{res.days}, {int(res.seconds / (60 * 60))} часов, {int(res.seconds % (60 * 60))} минут")

loop = asyncio.get_event_loop()
loop.run_until_complete(db_test())
