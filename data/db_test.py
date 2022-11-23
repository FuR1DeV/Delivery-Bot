import asyncio
from datetime import datetime

from sqlalchemy import and_

from data.commands import customers_get
from data.models.admins import Payment
from data.models.orders import Orders
from settings import config
from data.db_gino import db


async def db_test():
    pass
    await db.set_bind(config.POSTGRES_URI)

    payment = await Payment.query.where(Payment.user_id == 123).gino.first()
    if payment:
        await payment.delete()


loop = asyncio.get_event_loop()
loop.run_until_complete(db_test())
