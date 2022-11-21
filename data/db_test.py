import asyncio
from datetime import datetime

from sqlalchemy import and_

from data.commands import customers_get
from data.models.orders import Orders
from settings import config
from data.db_gino import db


async def db_test():
    pass
    await db.set_bind(config.POSTGRES_URI)

    result = await Orders.query.where(and_(Orders.user_id == 351490585,
                                           Orders.order_end.like("%11-2022%"))).gino.all()
    days = []
    for i in result:
        days.append(datetime.strptime(i.order_end, '%d-%m-%Y, %H:%M:%S').day)
    print(days)


loop = asyncio.get_event_loop()
loop.run_until_complete(db_test())
