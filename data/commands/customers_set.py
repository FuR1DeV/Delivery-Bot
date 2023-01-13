import logging

from data.models.customers import Customers
from data.models.orders import Orders, OrdersStatus, Reviews, OrdersLoading
from data.commands import customers_get, performers_get


logger = logging.getLogger("bot.data.commands.customer_set_db")

"""Функции добавления/обновления БД для Заказчика"""


async def customer_add(user_id, username, telephone, first_name, last_name):
    """Заказчик добавляется в БД"""
    customer = Customers(user_id=user_id, username=username, telephone=telephone, first_name=first_name,
                         last_name=last_name)
    await customer.create()


async def customer_add_order(user_id, geo_position_from, geo_position_to, title, price, description,
                             image, video, order_id, order_create, category_delivery, performer_category,
                             order_expired, order_worth):
    logger.info(f'Заказчик {user_id} добавляет заказ {order_id}')
    order = Orders(user_id=user_id, geo_position_from=geo_position_from, geo_position_to=geo_position_to, title=title,
                   price=price, description=description, image=image, video=video, order_id=order_id,
                   order_create=order_create, category_delivery=category_delivery,
                   performer_category=performer_category, order_expired=order_expired, order_worth=order_worth)
    customer = await Customers.query.where(Customers.user_id == user_id).gino.first()
    create = customer.create_orders + 1
    await customer.update(create_orders=create).apply()
    await order.create()


async def customer_add_order_loading(user_id, geo_position, description, price, image, video, order_id,
                                     order_create, order_expired, people):
    logger.info(f'Заказчик {user_id} добавляет заказ {order_id}')
    order = OrdersLoading(user_id=user_id, geo_position=geo_position, description=description, price=price,
                          image=image, video=video, order_id=order_id, order_create=order_create,
                          order_expired=order_expired, count_person=people)
    customer = await Customers.query.where(Customers.user_id == user_id).gino.first()
    create = customer.create_orders + 1
    await customer.update(create_orders=create).apply()
    await order.create()


async def update_customer_money(user_id, money):
    """Функция обновления баланса"""
    customer = await customers_get.customer_select(user_id)
    await customer.update(customer_money=money).apply()


async def customer_cancel_order(order_id, order_cancel):
    """Заказчик отменяет заказ"""
    order = await Orders.query.where(Orders.order_id == order_id).gino.first()
    order_loading = await OrdersLoading.query.where(OrdersLoading.order_id == order_id).gino.first()
    if order:
        order_status = await OrdersStatus.query.where(OrdersStatus.order_id == order_id).gino.first()
        await order.update(order_cancel=order_cancel, completed=None).apply()
        if order_status:
            await order_status.delete()
    if order_loading:
        await order_loading.update(order_cancel=order_cancel, completed=None).apply()


async def customer_set_order_status(order_id):
    """Заказчик ставит выполнено в состоянии заказа"""
    order_status = await OrdersStatus.query.where(OrdersStatus.order_id == order_id).gino.first()
    await order_status.update(customer_status=1).apply()


async def customer_set_rating_to_performer(user_id, input_customer):
    """Заказчик ставит оценку Исполнителю"""
    performer = await performers_get.performer_select(user_id)
    performer_rating = (performer.performer_rating + int(input_customer)) / 2
    await performer.update(performer_rating=performer_rating).apply()


async def customer_set_rating_to_performer_in_review_db(order_id, customer_rating):
    """Ставится оценка Исполнителю в таблицу Отзывы"""
    review = await Reviews.query.where(Reviews.order_id == order_id).gino.first()
    await review.update(rating_from_customer=int(customer_rating)).apply()


async def customer_set_review_to_performer_in_review_db(order_id, customer_review):
    """Заказчик оставляет отзыв Исполнителю в таблицу Отзывы"""
    review = await Reviews.query.where(Reviews.order_id == order_id).gino.first()
    await review.update(review_from_customer=customer_review).apply()


async def customer_set_block_order(order_id, block: int):
    order = await Orders.query.where(Orders.order_id == order_id).gino.first()
    order_loading = await OrdersLoading.query.where(OrdersLoading.order_id == order_id).gino.first()
    if order:
        await order.update(block=block).apply()
        return "order"
    if order_loading:
        await order_loading.update(block=block).apply()
        return "order_loading"


async def customer_change_order(order_id, change, result):
    logger.info(f'Заказчик редактирует {change}, заказ - {order_id}')
    order = await Orders.query.where(Orders.order_id == order_id).gino.first()
    order_loading = await OrdersLoading.query.where(OrdersLoading.order_id == order_id).gino.first()
    if change == "title":
        await order.update(title=result).apply()
    if change == "description":
        if order:
            await order.update(description=result).apply()
        if order_loading:
            await order_loading.update(description=result).apply()
    if change == "price":
        if order:
            await order.update(price=result).apply()
        if order_loading:
            await order_loading.update(price=result).apply()
    if change == "count_person":
        await order_loading.update(count_person=int(result)).apply()
    if change == "geo_position_from":
        await order.update(geo_position_from=result).apply()
    if change == "geo_position_to":
        await order.update(geo_position_to=result).apply()
