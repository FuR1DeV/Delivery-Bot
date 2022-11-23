import logging
from data.models.customers import Customers
from data.models.admins import Payment
from data.models.orders import Orders, OrdersStatus, Commission
from data.commands import customers_get


logger = logging.getLogger("bot.data.commands.general_set_db")

"""Функции взятия информации из БД общих запросов"""


async def all_customers():
    logger.info(f'Функция выгрузки всех заказчиков')
    customers = await Customers.query.gino.all()
    return customers


async def order_select(order_id):
    """Выбор заказа по order_id"""
    order = await Orders.query.where(Orders.order_id == order_id).gino.first()
    return order


async def check_details_status(order_id):
    """Выбор статуса заказа"""
    status = await OrdersStatus.query.where(OrdersStatus.order_id == order_id).gino.first()
    return status


async def check_commission_category(category):
    """Проверяется комиссия заказа определенной категории"""
    commission = await Commission.query.where(Commission.category == category).gino.first()
    return commission.commission


async def get_payment(bill_id):
    logger.info('Функция проверки платежа в БД')
    payment = Payment.query.where(Payment.bill_id == bill_id).gino.first()
    return payment








