import logging
from datetime import datetime

from data.models.customers import Customers
from data.models.performers import Performers
from data.models.orders import Orders, Reviews, OrdersStatus, Commission
from data.commands import customers_get, performers_get, general_get

logger = logging.getLogger("bot.data.commands.general_set_db")

"""Функции добавления/обновления БД общих запросов"""


async def add_review(order_id):
    logger.info(f'Добавляется возможность оставлять отзывы в заказе - {order_id}')
    review = Reviews(order_id=order_id)
    await review.create()


async def close_order_completed(order_id, order_end):
    """Помечается заказ как завершенный"""
    order = await Orders.query.where(Orders.order_id == order_id).gino.first()
    await order.update(completed=1, order_end=order_end).apply()


async def operation_commission(order):
    """Получаем комиссию из таблицы commission для определенной категории товаров и комиссию для Исполнителя"""
    commission_category = await general_get.check_commission_category(order.category_delivery)
    commission_for_performer = await Commission.query.where(Commission.category == "performers").gino.first()
    """Вычисляем комиссию"""
    res_commission_category = (int(order.price) * float(commission_category)) / 100
    res_commission_for_performer = ((int(order.price) * float(commission_for_performer.commission)) / 100) + res_commission_category
    """Взимаем комиссию с Заказчика"""
    """Временные промо со сниженным процентом"""
    # try:
    #     promo = global_db_obj.check_commission_promo(order[9])
    #     date_promo, percent_promo = str(promo[1]), promo[0]
    #     limitation = str(datetime.now() - datetime.strptime(date_promo, '%Y-%m-%d %H:%M:%S'))[:1]
    #     if limitation == "-":
    #         global_set_db_obj.set_commission_for_performer(order[9], float(percent_promo))
    #         # global_set_db_obj.set_commission_for_customer(order[1], res_commission_for_customer)
    #     if limitation != "-":
    #         global_set_db_obj.set_commission_for_performer(order[9], res_commission_for_performer)
    #         # global_set_db_obj.set_commission_for_customer(order[1], res_commission_for_customer)
    performer = await Performers.query.where(Performers.user_id == order.in_work).gino.first()
    money = float(performer.performer_money) - res_commission_for_performer
    await performer.update(performer_money=round(money, 2)).apply()


async def check_orders_status():
    orders_status = await OrdersStatus.query.gino.all()
    for i in orders_status:
        if i.performer_status + i.customer_status == 2:

            """Удаляется заказ из статуса при завершении с обоих сторон"""
            order_status = await OrdersStatus.query.where(OrdersStatus.order_id == i.order_id).gino.first()
            await order_status.delete()

            """Берется комиссия"""
            res_order = await performers_get.performer_view_order(i.order_id)
            await operation_commission(res_order)

            """Ставится пометка 1 в completed и datetime.now() завершения заказа в таблицу orders"""
            await close_order_completed(i.order_id, datetime.now().strftime('%d-%m-%Y, %H:%M:%S'))
    return orders_status


async def create_commission():
    """Создается БД комиссий с дефолтными значениями"""
    commission_query = await Commission.query.gino.all()
    if commission_query:
        return
    else:
        cat = {
            "performers": "3.7",
            "Цветы": "2.1",
            "Подарки": "2.2",
            "Кондитерка": "2.3",
            "Документы": "2.4",
            "Погрузка/Разгрузка": "2.5",
            "Другое": "2.6"
        }
        for k, v in cat.items():
            commission = Commission(category=k, commission=v)
            await commission.create()
