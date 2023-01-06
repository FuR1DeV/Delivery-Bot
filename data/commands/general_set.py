import logging
from datetime import datetime

from data.models.performers import Performers
from data.models.admins import Payment, PrivateChat
from data.models.orders import Orders, Reviews, OrdersStatus, Commission, CommissionPromo
from data.commands import performers_get, general_get

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
    res_commission_for_performer = ((int(order.price) *
                                     float(commission_for_performer.commission)) / 100) + res_commission_category
    """Взимаем комиссию с Заказчика"""
    """Временные промо со сниженным процентом"""
    performer = await Performers.query.where(Performers.user_id == order.in_work).gino.first()
    money = float(performer.performer_money) - res_commission_for_performer
    promo = await general_get.check_commission_promo(order.in_work)
    if promo:
        res_commission_for_performer = ((int(order.price) * float(promo.percent)) / 100)
        money = float(performer.performer_money) - res_commission_for_performer
    await performer.update(performer_money=round(money, 2)).apply()


async def check_orders_status():
    orders_status = await OrdersStatus.query.gino.all()
    promo = await CommissionPromo.query.gino.all()
    for i in promo:
        limitation = str(datetime.now() - i.promo_time)[:1]
        if limitation != "-":
            await delete_expired_promo(i.user_id)
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


async def get_payment_exists_and_delete(user_id):
    """Функция проверки возможных остатков в БД"""
    payment = await Payment.query.where(Payment.user_id == user_id).gino.first()
    """А затем удаление из БД"""
    if payment:
        await payment.delete()


async def add_payment(user_id, money, bill_id):
    logger.info(f'{user_id} Добавляет платеж {money} в БД, bill_id - {bill_id}')
    payment = Payment(user_id=user_id, money=money, bill_id=bill_id)
    await payment.create()


async def delete_payment(user_id):
    """Функция удаления платежа из БД"""
    logger.info(f'Пользователь {user_id} отменяет пополнение баланса')
    payment = await Payment.query.where(Payment.user_id == user_id).gino.first()
    await payment.delete()


async def order_rating_change_plus(order_id):
    order = await Orders.query.where(Orders.order_id == order_id).gino.first()
    order_rate = order.order_rating + 1
    await order.update(order_rating=order_rate).apply()


async def order_rating_change_minus(order_id):
    order = await Orders.query.where(Orders.order_id == order_id).gino.first()
    order_rate = order.order_rating - 1
    await order.update(order_rating=order_rate).apply()


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


async def delete_order_expired(order_id):
    order = await Orders.query.where(Orders.order_id == order_id).gino.first()
    logger.info(f'Система удаляет заказ {order_id}. Время заказа истекло')
    await order.delete()


async def private_chat_delete_user(user_id):
    user = await PrivateChat.query.where(PrivateChat.user_id == user_id).gino.first()
    await user.delete()


async def private_chat_change_count_word(user_id):
    user = await PrivateChat.query.where(PrivateChat.user_id == user_id).gino.first()
    await user.update(count_word=user.count_word + 1)


async def delete_expired_promo(user_id):
    promo = await CommissionPromo.query.where(CommissionPromo.user_id == user_id).gino.first()
    await promo.delete()
