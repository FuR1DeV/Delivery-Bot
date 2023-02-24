import logging

from data.models.customers import Customers
from data.models.performers import Performers, JobsSales
from data.models.admins import Admins
from data.models.orders import Commission, CommissionPromo

logger = logging.getLogger("bot.data.commands.customer_set_db")

"""Функции добавления/обновления БД для Заказчика"""


async def admin_add(user_id, username, first_name, last_name):
    """Админ добавляется в БД"""
    admin = Admins(user_id=user_id, username=username, first_name=first_name, last_name=last_name)
    await admin.create()


async def block_user(block, type_user, user_id):
    if block:
        logger.info(f'Администратор блокирует пользователя {user_id}')
        if type_user == "performers":
            performer = await Performers.query.where(Performers.user_id == user_id).gino.first()
            await performer.update(ban=1).apply()
        else:
            customer = await Customers.query.where(Customers.user_id == user_id).gino.first()
            await customer.update(ban=1).apply()
    else:
        logger.info(f'Администратор разблокирует пользователя {user_id}')
        if type_user == "performers":
            performer = await Performers.query.where(Performers.user_id == user_id).gino.first()
            await performer.update(ban=0).apply()
        else:
            customer = await Customers.query.where(Customers.user_id == user_id).gino.first()
            await customer.update(ban=0).apply()


async def admin_set_money(user_id, money):
    logger.info(f'Админ добавляет деньги {money} для {user_id}')
    performer = await Performers.query.where(Performers.user_id == user_id).gino.first()
    await performer.update(performer_money=performer.performer_money + money).apply()


async def admin_set_rating(user_id, rating):
    logger.info(f'Админ обновляет рейтинг {rating} для {user_id}')
    performer = await Performers.query.where(Performers.user_id == user_id).gino.first()
    await performer.update(performer_rating=rating).apply()


async def admin_set_commission_for_performer(res):
    logger.info('Админ устанавливает комиссию для Исполнителя')
    commission = await Commission.query.where(Commission.category == "performers").gino.first()
    await commission.update(commission=res).apply()


async def admin_set_commission_for_categories(category, res):
    logger.info(f'Админ устанавливает комиссию для {category} в размере {res}')
    if category == "Цветы":
        commission = await Commission.query.where(Commission.category == "Цветы").gino.first()
        await commission.update(commission=res).apply()
    if category == "Подарки":
        commission = await Commission.query.where(Commission.category == "Подарки").gino.first()
        await commission.update(commission=res).apply()
    if category == "Кондитерка":
        commission = await Commission.query.where(Commission.category == "Кондитерка").gino.first()
        await commission.update(commission=res).apply()
    if category == "Документы":
        commission = await Commission.query.where(Commission.category == "Документы").gino.first()
        await commission.update(commission=res).apply()
    if category == "Погрузка/Разгрузка":
        commission = await Commission.query.where(Commission.category == "Погрузка/Разгрузка").gino.first()
        await commission.update(commission=res).apply()
    if category == "Другое":
        commission = await Commission.query.where(Commission.category == "Другое").gino.first()
        await commission.update(commission=res).apply()


async def set_commission_for_promo(user_id, percent, promo_time):
    logger.info(f'Добавляется временное промо для {user_id} '
                f'комиссия - {percent}, время - {promo_time}')
    commission = CommissionPromo(user_id=user_id, percent=percent, promo_time=promo_time)
    await commission.create()


async def jobs_sales(jobs, value):
    if jobs == "auto_send":
        auto_send = await JobsSales.query.where(JobsSales.jobs == "auto_send").gino.first()
        await auto_send.update(value=value).apply()
    if jobs == "twelve":
        twelve = await JobsSales.query.where(JobsSales.jobs == "twelve").gino.first()
        await twelve.update(value=value).apply()
    if jobs == "day":
        day = await JobsSales.query.where(JobsSales.jobs == "day").gino.first()
        await day.update(value=value).apply()
    if jobs == "3_day":
        day = await JobsSales.query.where(JobsSales.jobs == "3_day").gino.first()
        await day.update(value=value).apply()
    if jobs == "week":
        week = await JobsSales.query.where(JobsSales.jobs == "week").gino.first()
        await week.update(value=value).apply()
