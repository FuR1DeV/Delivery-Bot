import logging
from data.models.customers import Customers
from data.models.performers import Performers
from data.models.admins import Payment, PrivateChat
from data.models.orders import Orders, OrdersStatus, Commission, Reviews, CommissionPromo, OrdersLoading

logger = logging.getLogger("bot.data.commands.general_set_db")

"""Функции взятия информации из БД общих запросов"""


async def all_customers():
    logger.info(f'Функция выгрузки всех Заказчиков')
    customers = await Customers.query.gino.all()
    return customers


async def all_performers():
    logger.info(f'Функция выгрузки всех Исполнителей')
    performers = await Performers.query.gino.all()
    return performers


async def all_performers_auto_send():
    logger.info(f'Функция выгрузки всех Исполнителей с автоматической отправкой')
    performers = await Performers.query.where(Performers.auto_send == 1).gino.all()
    return performers


async def all_orders():
    logger.info(f'Функция выгрузки всех Заказов')
    orders = await Orders.query.gino.all()
    return orders


async def all_completed_orders():
    orders = await Orders.query.where(Orders.completed == 1).gino.all()
    return orders


async def all_orders_reviews():
    logger.info(f'Функция просмотра всех отзывов')
    reviews = await Reviews.query.gino.all()
    return reviews


async def order_select(order_id):
    """Выбор заказа по order_id"""
    order = await Orders.query.where(Orders.order_id == order_id).gino.first()
    return order


async def order_select_loading(order_id):
    """Выбор заказа погрузки по order_id"""
    order = await OrdersLoading.query.where(OrdersLoading.order_id == order_id).gino.first()
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


async def check_orders_expired():
    orders = await Orders.query.where(Orders.in_work == 0).gino.all()
    return orders


async def check_orders_loading_expired():
    orders_loading = await OrdersLoading.query.where(OrdersLoading.persons_list == []).gino.all()
    return orders_loading


async def check_private_chat_count_word(user_id):
    user = await PrivateChat.query.where(PrivateChat.user_id == user_id).gino.first()
    return user.count_word


async def check_commission_promo(user_id):
    promo = await CommissionPromo.query.where(CommissionPromo.user_id == user_id).gino.first()
    return promo
