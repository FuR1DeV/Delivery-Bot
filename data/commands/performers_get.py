import logging

from sqlalchemy import and_, or_

from data.models.orders import Orders, OrdersRating, OrdersStatus, OrdersLoading, CommissionPromo
from data.models.performers import Performers, PerformerPersonalData, AutoSendJobOffer, JobsSales, JobsOffers
from data.models.admins import PrivateChat

logger = logging.getLogger("bot.data.commands.performer_get_db")

"""Функции взятия информации из БД"""


async def performer_select(user_id):
    """Выбор Исполнителя"""
    performer = await Performers.query.where(Performers.user_id == user_id).gino.first()
    return performer


async def performer_select_personal_data(user_id):
    performer = await PerformerPersonalData.query.where(PerformerPersonalData.user_id == user_id).gino.first()
    return performer


async def performer_count_orders(user_id) -> tuple:
    """Исполнитель смотрит статистику по заказам"""
    performer = await Performers.query.where(Performers.user_id == user_id).gino.first()
    orders_in_work = await Orders.query.where(and_(Orders.in_work == user_id,
                                                   Orders.completed == 0)).gino.all()
    return performer, len(orders_in_work)


async def check_private_chat_status(user_id):
    """Исполнитель проверяет статус приватного чата"""
    private = await PrivateChat.query.where(PrivateChat.user_id == user_id).gino.first()
    return private


async def performer_checks_all_orders(user_id, performer_category):
    """Исполнитель смотрит все заказы"""
    orders = await Orders.query.where(and_(Orders.in_work == 0,
                                           Orders.block == 0,
                                           Orders.order_get == None,
                                           Orders.user_id != user_id,
                                           or_(Orders.performer_category == performer_category,
                                               Orders.performer_category == 'any'))).gino.all()
    return orders


async def performer_checks_all_orders_loading(user_id):
    """Исполнитель смотрит все заказы Погрузки/Разгрузки"""
    orders = await OrdersLoading.query.where(and_(OrdersLoading.block == 0,
                                                  OrdersLoading.order_end == None,
                                                  OrdersLoading.user_id != user_id,
                                                  OrdersLoading.person != OrdersLoading.count_person)).gino.all()
    return orders


async def performer_check_order_loading(order_id):
    order_loading = await OrdersLoading.query.where(OrdersLoading.order_id == order_id).gino.first()
    return order_loading


async def performer_check_order_loading_relevance(user_id, order_id):
    order_loading = await OrdersLoading.query.where(OrdersLoading.order_id == order_id).gino.first()
    if user_id in order_loading.persons_list:
        return order_loading


async def performer_checks_all_orders_with_category(user_id, performer_category, category_delivery):
    """Исполнитель смотрит все заказы с определенной категорией"""
    orders = await Orders.query.where(and_(Orders.in_work == 0,
                                           Orders.block == 0,
                                           Orders.order_get == None,
                                           Orders.user_id != user_id,
                                           or_(Orders.performer_category == performer_category,
                                               Orders.performer_category == 'any'),
                                           Orders.category_delivery == category_delivery)).gino.all()
    return orders


async def performer_loader_order(user_id):
    """Исполнитель смотрит все свои заказы Погрузки/Разгрузки"""
    orders_loading = await OrdersLoading.query.where(OrdersLoading.order_end == None).gino.all()
    res_orders = [i for i in orders_loading if user_id in i.persons_list]
    return res_orders


async def performer_check_order_rating(order_id, user_id):
    """Исполнитель смотрит рейтинг заказа"""
    order = await OrdersRating.query.where(and_(OrdersRating.order_id == order_id,
                                                OrdersRating.user_id == user_id)).gino.first()
    if order is None:
        return None
    else:
        return order.rating


async def performer_view_order(order_id):
    """Исполнитель смотрит заказ по order_id"""
    order = await Orders.query.where(Orders.order_id == order_id).gino.first()
    return order


async def performer_checks_customer_user_id(order_id):
    """Исполнитель смотрит user_id Заказчика по order_id"""
    user = await Orders.query.where(Orders.order_id == order_id).gino.first()
    return user.user_id


async def performer_view_list_orders(user_id):
    """Исполнитель просматривает взятые заказы"""
    orders = await Orders.query.where(and_(Orders.in_work == user_id,
                                           Orders.completed == 0)).gino.all()
    return orders


async def performer_get_status_order(order_id):
    """Исполнитель просматривает есть ли заказ в orders_status"""
    order_status = await OrdersStatus.query.where(OrdersStatus.order_id == order_id).gino.first()
    if order_status:
        return True
    else:
        return None


async def performer_all_completed_orders(user_id):
    """Исполнитель выгружает список всех своих завершенных заказов"""
    orders = await Orders.query.where(and_(Orders.in_work == user_id,
                                           Orders.completed == 1)).gino.all()
    return orders


async def performer_get_finished_orders_year(user_id, year):
    """Исполнитель выгружает список всех своих завершенных заказов"""
    """Выбирает год"""
    result = await Orders.query.where(and_(Orders.in_work == user_id,
                                           Orders.order_end.like(f"%{year}%"))).gino.all()
    return result


async def performer_get_finished_orders_month(user_id, year, month):
    """Исполнитель выгружает список всех своих завершенных заказов"""
    """Выбирает месяц"""
    result = await Orders.query.where(and_(Orders.in_work == user_id,
                                           Orders.order_end.like(f"%{month}-{year}%"))).gino.all()
    return result


async def performer_get_finished_orders_day(user_id, year, month, day):
    """Исполнитель выгружает список всех своих завершенных заказов"""
    """Выбирает день"""
    result = await Orders.query.where(and_(Orders.in_work == user_id,
                                           Orders.order_end.like(f"%{day}-{month}-{year}%"))).gino.all()
    return result


async def performer_get_complete_order(order_id):
    """Исполнитель выгружает конкретный завершенный заказ"""
    order = await Orders.query.where(and_(Orders.order_id == order_id,
                                          Orders.completed == 1)).gino.first()
    return order


async def performer_trying_change_self_category(user_id):
    performer = await Performers.query.where(Performers.user_id == user_id).gino.first()
    return performer.performer_category_limit


async def performer_arrive_info(order_id):
    arrive = await OrdersStatus.query.where(OrdersStatus.order_id == order_id).gino.first()
    return arrive.performer_arrive


async def performer_auto_send_check(user_id):
    performer = await AutoSendJobOffer.query.where(AutoSendJobOffer.user_id == user_id).gino.first()
    return performer


async def check_commission_promo(user_id):
    commission = await CommissionPromo.query.where(CommissionPromo.user_id == user_id).gino.first()
    return commission


async def check_job_sale(job):
    job = await JobsSales.query.where(JobsSales.jobs == job).gino.first()
    return job


async def performer_check_jobs_offers(user_id):
    exist = await JobsOffers.query.where(JobsOffers.user_id == user_id).gino.first()
    return exist
