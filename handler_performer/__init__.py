__all__ = ["register_performer"]

from aiogram import Dispatcher

from .performer_1_main import PerformerMain, PerformerProfile
from .performer_2_tasks import PerformerTasks, PerformerDetailsTasks, PerformerDetailsTasksStatus
from .performer_3_history import PerformerHistory
from .performer_4_help import PerformerHelp
from states import performer_states


def register_performer(disp: Dispatcher):
    # performer_main
    disp.register_message_handler(PerformerMain.phone,
                                  content_types=['contact'],
                                  state=performer_states.PerformerPhone.phone)
    disp.register_callback_query_handler(PerformerMain.hi_performer, text='performer')
    disp.register_message_handler(PerformerMain.performer_menu,
                                  content_types=['text', 'location'],
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
    disp.register_message_handler(PerformerMain.orders,
                                  state=performer_states.PerformerStart.orders)
    disp.register_message_handler(PerformerMain.info_about_performer_name,
                                  state=performer_states.PerformerRegister.name)
    disp.register_message_handler(PerformerMain.info_about_performer_surname,
                                  state=performer_states.PerformerRegister.surname)
    disp.register_message_handler(PerformerMain.info_about_performer_selfie,
                                  content_types=['photo', 'text'],
                                  state=performer_states.PerformerRegister.photo)
    disp.register_message_handler(PerformerMain.info_about_performer_geo_position,
                                  content_types=['location', 'text'],
                                  state=performer_states.PerformerRegister.geo_position)
    disp.register_message_handler(PerformerMain.jobs_offers,
                                  state=performer_states.PerformerJobsOffers.enter)
    disp.register_callback_query_handler(PerformerMain.approve_jobs_offers,
                                         text_contains="jobs-",
                                         state=["*"])

    # performer_profile
    disp.register_message_handler(PerformerProfile.performer_profile,
                                  state=performer_states.PerformerProfile.my_profile)
    disp.register_message_handler(PerformerProfile.performer_profile_change_status,
                                  state=performer_states.PerformerProfile.change_status)
    disp.register_message_handler(PerformerProfile.pay,
                                  state=performer_states.PerformerProfile.pay)
    disp.register_callback_query_handler(PerformerProfile.check,
                                         text_contains='check_',
                                         state=performer_states.PerformerProfile.pay)
    disp.register_callback_query_handler(PerformerProfile.cancel,
                                         text='cancel_pay',
                                         state=performer_states.PerformerProfile.pay)
    disp.register_callback_query_handler(PerformerProfile.auto_send_job_offer,
                                         text_contains='auto_send_pay_',
                                         state=["*"])
    disp.register_callback_query_handler(PerformerProfile.change_status_category,
                                         text_contains='performer_change_status',
                                         state=["*"])
    disp.register_callback_query_handler(PerformerProfile.delete_message,
                                         text='delete_message',
                                         state=["*"])

    # performer_tasks
    disp.register_message_handler(PerformerTasks.check_all_orders,
                                  state=performer_states.PerformerTasks.check_all_orders)
    disp.register_callback_query_handler(PerformerTasks.order_request,
                                         state=["*"],
                                         text_contains='order_request_')
    disp.register_callback_query_handler(PerformerTasks.proposal,
                                         state=["*"],
                                         text_contains='order_proposal_')
    disp.register_message_handler(PerformerTasks.proposal_price,
                                  state=performer_states.PerformerTasks.proposal)
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
    disp.register_message_handler(PerformerTasks.loading_request_approve,
                                  state=performer_states.PerformerTasks.loading_request)

    # performer_details_tasks
    disp.register_message_handler(PerformerDetailsTasks.performer_details,
                                  state=performer_states.PerformerDetailsTasks.details_tasks)
    disp.register_message_handler(PerformerDetailsTasks.detail_task,
                                  state=performer_states.PerformerDetailsTasks.enter_task,
                                  content_types=['text', 'video_note', 'voice'])
    disp.register_message_handler(PerformerDetailsTasks.performer_details_loading,
                                  state=performer_states.PerformerDetailsTasks.loading_tasks)
    disp.register_message_handler(PerformerDetailsTasks.performer_details_loading_enter,
                                  state=performer_states.PerformerDetailsTasks.enter_loading_task,
                                  content_types=['text', 'video_note', 'voice'])

    # performer_details_tasks_status
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

    # performer_help
    disp.register_message_handler(PerformerHelp.performer_help,
                                  content_types=['text', 'video_note',
                                                 'voice', 'video', 'photo'],
                                  state=performer_states.PerformerHelp.help)
    disp.register_callback_query_handler(PerformerHelp.performer_private_chat,
                                         text='private_chat',
                                         state=performer_states.PerformerHelp.help)

    # performer_history
    disp.register_message_handler(PerformerHistory.history, state=performer_states.PerformerHistory.enter_history)
    disp.register_message_handler(PerformerHistory.order_history,
                                  state=performer_states.PerformerHistory.order_history)
    disp.register_message_handler(PerformerHistory.order_details,
                                  state=performer_states.PerformerHistory.order_history_details)
