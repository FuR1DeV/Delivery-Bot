__all__ = ["register_admin_handler"]

from aiogram import Dispatcher

from .admin import AdminMain, AdminOrders, AdminStats, AdminCommission, AdminControlChange, AdminControl, AdminJobs
from states import states


def register_admin_handler(disp: Dispatcher):
    disp.register_message_handler(AdminMain.admin_main, state=states.AdminStates.enter)
    disp.register_message_handler(AdminMain.loading_db, state=states.AdminStates.loading_db)

    # def register_orders_handler(disp: Dispatcher):
    disp.register_message_handler(AdminOrders.enter_orders, state=states.Orders.enter)
    disp.register_message_handler(AdminOrders.order, state=states.Orders.order)
    disp.register_message_handler(AdminOrders.order_details, state=states.Orders.detail_order)

    # def register_orders_handler(disp: Dispatcher):
    disp.register_message_handler(AdminStats.stat_main, state=states.Statistics.enter)

    # def register_commission_handler(disp: Dispatcher):
    disp.register_message_handler(AdminCommission.commission, state=states.Commission.commission)
    disp.register_message_handler(AdminCommission.commission_set, state=states.Commission.commission_set)
    disp.register_message_handler(AdminCommission.commission_for_performer,
                                  state=states.Commission.commission_for_performer)
    disp.register_message_handler(AdminCommission.commission_for_categories,
                                  state=states.CommissionForCategories.commission_for_categories)
    disp.register_message_handler(AdminCommission.commission_for,
                                  state=states.CommissionForCategories.commission_for_category)
    disp.register_message_handler(AdminCommission.commission_promo,
                                  state=states.Commission.commission_promo)
    disp.register_message_handler(AdminCommission.commission_promo_find_id,
                                  state=states.Commission.commission_promo_find_id)
    disp.register_callback_query_handler(AdminCommission.commission_promo_set_discount,
                                         state=states.Commission.commission_promo_set_discount,
                                         text_contains='commission_')
    disp.register_callback_query_handler(AdminCommission.commission_promo_set_time,
                                         state=states.Commission.commission_promo_set_discount,
                                         text_contains='time_')

    # def register_control_change_handler(disp: Dispatcher):
    disp.register_message_handler(AdminControlChange.change_main, state=states.ChangeUsers.enter)
    disp.register_message_handler(AdminControlChange.add_money, state=states.ChangeUsers.add_money)
    disp.register_message_handler(AdminControlChange.change_rating, state=states.ChangeUsers.rating)

    # def register_control_handler(disp: Dispatcher):
    disp.register_message_handler(AdminControl.control, state=states.AboutUsers.enter)
    disp.register_message_handler(AdminControl.find_id, state=states.AboutUsers.find_id)
    disp.register_message_handler(AdminControl.find_first_name, state=states.AboutUsers.find_first_name)
    disp.register_message_handler(AdminControl.find_username, state=states.AboutUsers.find_username)
    disp.register_message_handler(AdminControl.find_telephone, state=states.AboutUsers.find_telephone)

    disp.register_message_handler(AdminJobs.jobs, state=states.AdminStates.jobs)
