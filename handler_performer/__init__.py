__all__ = ["register_performer"]

from aiogram import Dispatcher

from .performer import PerformerMain, PerformerProfile, PerformerTasks, PerformerDetailsTasks, \
    PerformerDetailsTasksStatus, PerformerHelp, PerformerHistory
from states import performer_states


def register_performer(disp: Dispatcher):
    disp.register_message_handler(PerformerMain.phone, content_types=['contact'],
                                  state=performer_states.PerformerPhone.phone)
    disp.register_callback_query_handler(PerformerMain.hi_performer, text='performer')
    disp.register_message_handler(PerformerMain.performer_menu,
                                  state=performer_states.PerformerStart.performer_menu)
    disp.register_callback_query_handler(PerformerMain.choose_month,
                                         state=performer_states.PerformerStart.performer_menu,
                                         text_contains='p_year_finish_')
    disp.register_callback_query_handler(PerformerMain.choose_day,
                                         state=performer_states.PerformerStart.performer_menu,
                                         text_contains='p_month_finish_')
    disp.register_callback_query_handler(PerformerMain.choose_job,
                                         state=performer_states.PerformerStart.performer_menu,
                                         text_contains='p_day_finish_')

    # def register_performer_profile(disp: Dispatcher):
    disp.register_message_handler(PerformerProfile.performer_profile,
                                  state=performer_states.PerformerProfile.my_profile)
    disp.register_message_handler(PerformerProfile.performer_profile_change_status,
                                  state=performer_states.PerformerProfile.change_status)
    disp.register_message_handler(PerformerProfile.transport,
                                  state=performer_states.PerformerProfile.change_status_transport)
    disp.register_message_handler(PerformerProfile.pay,
                                  state=performer_states.PerformerProfile.pay)
    disp.register_callback_query_handler(PerformerProfile.check,
                                         text_contains='check_',
                                         state=performer_states.PerformerProfile.pay)
    disp.register_callback_query_handler(PerformerProfile.cancel,
                                         text='cancel_pay',
                                         state=performer_states.PerformerProfile.pay)

    # def register_performer_tasks(disp: Dispatcher):
    disp.register_message_handler(PerformerTasks.check_all_orders,
                                  state=performer_states.PerformerTasks.check_all_orders)
    disp.register_message_handler(PerformerTasks.get_order,
                                  state=performer_states.PerformerTasks.get_order)
    disp.register_callback_query_handler(PerformerTasks.order_request,
                                         state=performer_states.PerformerTasks.approve_or_decline,
                                         text='performer_request')
    disp.register_callback_query_handler(PerformerTasks.approve_order, state=["*"],
                                         text='performer_get')
    disp.register_callback_query_handler(PerformerTasks.decline_order,
                                         state=["*"],
                                         text='performer_decline')
    disp.register_callback_query_handler(PerformerTasks.proposal,
                                         state=performer_states.PerformerTasks.approve_or_decline,
                                         text='performer_proposal')
    disp.register_message_handler(PerformerTasks.proposal_price,
                                  state=performer_states.PerformerTasks.proposal)
    disp.register_callback_query_handler(PerformerTasks.approve_order_with_new_price,
                                         state=["*"],
                                         text='performer_get_with_new_price')
    disp.register_callback_query_handler(PerformerTasks.choose_category,
                                         state=performer_states.PerformerTasks.check_all_orders,
                                         text_contains="cat_")
    disp.register_callback_query_handler(PerformerTasks.order_rating_plus,
                                         state=performer_states.PerformerTasks.check_all_orders,
                                         text_contains="plus_")
    disp.register_callback_query_handler(PerformerTasks.order_rating_minus,
                                         state=performer_states.PerformerTasks.check_all_orders,
                                         text_contains="minus_")
    disp.register_callback_query_handler(PerformerTasks.order_loading_into_yes,
                                         state=["*"],
                                         text_contains="yes_req_load_")
    disp.register_callback_query_handler(PerformerTasks.loading_request,
                                         state=["*"],
                                         text_contains="request_loading_")
    disp.register_callback_query_handler(PerformerTasks.loading_request_decline,
                                         state=["*"],
                                         text="decline_loading")

    # def register_performer_details_tasks(disp: Dispatcher):
    disp.register_message_handler(PerformerDetailsTasks.performer_details,
                                  state=performer_states.PerformerDetailsTasks.details_tasks)
    disp.register_message_handler(PerformerDetailsTasks.detail_task,
                                  state=performer_states.PerformerDetailsTasks.enter_task)

    # def register_performer_details_tasks_status(disp: Dispatcher):
    disp.register_message_handler(PerformerDetailsTasksStatus.details_status,
                                  state=performer_states.PerformerDetailsTasksStatus.enter_status)
    disp.register_callback_query_handler(PerformerDetailsTasksStatus.cancel_order,
                                         text="cancel",
                                         state=performer_states.PerformerDetailsTasksStatus.enter_status)
    disp.register_callback_query_handler(PerformerDetailsTasksStatus.no_cancel_order,
                                         text="no_cancel",
                                         state=performer_states.PerformerDetailsTasksStatus.enter_status)
    disp.register_callback_query_handler(PerformerDetailsTasksStatus.close_order,
                                         text="close_order",
                                         state=performer_states.PerformerDetailsTasksStatus.enter_status)
    disp.register_callback_query_handler(PerformerDetailsTasksStatus.no_close,
                                         text="no_close",
                                         state=performer_states.PerformerDetailsTasksStatus.enter_status)
    disp.register_message_handler(PerformerDetailsTasksStatus.rating,
                                  state=performer_states.PerformerDetailsTasksStatus.rating)
    disp.register_message_handler(PerformerDetailsTasksStatus.review,
                                  state=performer_states.PerformerDetailsTasksStatus.review)

    # def register_performer_help(disp: Dispatcher):
    disp.register_message_handler(PerformerHelp.performer_help,
                                  content_types=['text'],
                                  state=performer_states.PerformerHelp.help)
    disp.register_message_handler(PerformerHelp.performer_upload_photo,
                                  content_types=['photo', 'text'],
                                  state=performer_states.PerformerHelp.upload_photo)
    disp.register_message_handler(PerformerHelp.performer_upload_video,
                                  content_types=['video', 'text'],
                                  state=performer_states.PerformerHelp.upload_video)
    disp.register_callback_query_handler(PerformerHelp.performer_private_chat,
                                         text='private_chat',
                                         state=performer_states.PerformerHelp.help)

    # def register_performer_history(disp: Dispatcher):
    disp.register_message_handler(PerformerHistory.history, state=performer_states.PerformerHistory.enter_history)
    disp.register_message_handler(PerformerHistory.order_history,
                                  state=performer_states.PerformerHistory.order_history)
    disp.register_message_handler(PerformerHistory.order_details,
                                  state=performer_states.PerformerHistory.order_history_details)
