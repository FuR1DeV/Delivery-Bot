import asyncio

from data.models.orders import Orders
from settings import config
from data.db_gino import db


async def db_test():
    pass
    await db.set_bind(config.POSTGRES_URI)
    # await db.gino.drop_all()
    # await db.gino.create_all()

    # await commands.add_customer(user_id=23423, username="vass", telephone="+7923", first_name="VAS",
    #                             last_name="TUR", customer_money="92", customer_rating="4", ban=0, create_orders=4,
    #                             canceled_orders=44)

    customer = await Orders.query.where(Orders.user_id == 34234).gino.all()
    print(customer)

loop = asyncio.get_event_loop()
loop.run_until_complete(db_test())

