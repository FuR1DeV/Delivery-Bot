__all__ = ["register_customer"]

from aiogram import Dispatcher
from .customer_1_main import CustomerMain, CustomerProfile
from .customer_2_create_task import CustomerCreateTaskLoading, CustomerCreateTask
from .customer_3_details_task import CustomerDetailsTasks, CustomerDetailsTasksChange, CustomerDetailsTasksStatus
from .customer_4_history import CustomerHistory
from .customer_5_help import CustomerHelp
from states import customer_states


def register_customer(disp: Dispatcher):
    disp.register_message_handler(CustomerMain.phone, content_types=['contact'],
                                  state=customer_states.CustomerPhone.phone)
    disp.register_callback_query_handler(CustomerMain.hi_customer, text='customer')
    disp.register_message_handler(CustomerMain.main, state=customer_states.CustomerStart.start)
    disp.register_message_handler(CustomerMain.customer_menu, state=customer_states.CustomerStart.customer_menu)
    disp.register_callback_query_handler(CustomerMain.customer_approve,
                                         state=["*"],
                                         text_contains='-customer_yes-')
    disp.register_callback_query_handler(CustomerMain.customer_decline,
                                         state=["*"],
                                         text='customer_no')
    disp.register_callback_query_handler(CustomerMain.customer_view_perf_profile,
                                         state=["*"],
                                         text_contains='customer_view_perf_profile_')
    disp.register_callback_query_handler(CustomerMain.customer_view_photo,
                                         state=["*"],
                                         text_contains='customer_view_photo_')
    disp.register_callback_query_handler(CustomerMain.customer_view_video,
                                         state=["*"],
                                         text_contains='customer_view_video_')
    disp.register_callback_query_handler(CustomerMain.proposal_from_performer_yes, state=["*"], text='proposal_yes')
    disp.register_callback_query_handler(CustomerMain.proposal_from_performer_no, state=["*"], text='proposal_no')
    disp.register_callback_query_handler(CustomerMain.choose_month,
                                         state=customer_states.CustomerStart.customer_menu,
                                         text_contains='year_finish_')
    disp.register_callback_query_handler(CustomerMain.choose_day,
                                         state=customer_states.CustomerStart.customer_menu,
                                         text_contains='month_finish_')
    disp.register_callback_query_handler(CustomerMain.choose_job,
                                         state=customer_states.CustomerStart.customer_menu,
                                         text_contains='day_finish_')
    disp.register_callback_query_handler(CustomerMain.refresh,
                                         state=["*"], text='refresh')
    disp.register_callback_query_handler(CustomerMain.approve_info_arrived,
                                         state=["*"], text_contains='arrive_approve_')
    disp.register_message_handler(CustomerMain.orders,
                                  state=customer_states.CustomerStart.orders)
    disp.register_callback_query_handler(CustomerMain.refresh_loading,
                                         state=["*"], text="refresh_loading")
    disp.register_callback_query_handler(CustomerMain.cancel,
                                         state=["*"], text="perf_cancel")

    # def register_customer_profile(disp: Dispatcher):
    disp.register_message_handler(CustomerProfile.customer_profile,
                                  state=customer_states.CustomerProfile.my_profile)

    # def register_customer_create_task(disp: Dispatcher):
    disp.register_message_handler(CustomerCreateTask.category_delivery,
                                  state=customer_states.CustomerCreateTask.category_delivery)
    disp.register_message_handler(CustomerCreateTask.geo_position_from,
                                  content_types=['location', 'text', 'web_app_data'],
                                  state=customer_states.CustomerCreateTask.geo_position_from)
    disp.register_callback_query_handler(CustomerCreateTask.approve_geo_from,
                                         text="approve_geo_from",
                                         state=customer_states.CustomerCreateTask.geo_position_from)
    disp.register_message_handler(CustomerCreateTask.geo_position_to,
                                  content_types=['location', 'text', 'web_app_data'],
                                  state=customer_states.CustomerCreateTask.geo_position_to)
    disp.register_callback_query_handler(CustomerCreateTask.approve_geo_to,
                                         text="approve_geo_to",
                                         state=customer_states.CustomerCreateTask.geo_position_to)
    disp.register_message_handler(CustomerCreateTask.description,
                                  state=customer_states.CustomerCreateTask.description)
    disp.register_message_handler(CustomerCreateTask.price,
                                  state=customer_states.CustomerCreateTask.price)
    disp.register_message_handler(CustomerCreateTask.performer_category,
                                  state=customer_states.CustomerCreateTask.performer_category)
    disp.register_message_handler(CustomerCreateTask.photo_video,
                                  state=customer_states.CustomerCreateTask.photo_or_video)
    disp.register_message_handler(CustomerCreateTask.photo, content_types=['photo', 'text'],
                                  state=customer_states.CustomerCreateTask.photo)
    disp.register_message_handler(CustomerCreateTask.video, content_types=['video', 'text'],
                                  state=customer_states.CustomerCreateTask.video)
    disp.register_message_handler(CustomerCreateTask.expired_order,
                                  state=customer_states.CustomerCreateTask.expired_data)
    disp.register_message_handler(CustomerCreateTask.order_worth,
                                  state=customer_states.CustomerCreateTask.worth)

    # def register_customer_create_task_loading(disp: Dispatcher):
    disp.register_message_handler(CustomerCreateTaskLoading.geo_position_from,
                                  content_types=['location', 'text'],
                                  state=customer_states.CustomerCreateTaskLoading.geo_position)
    disp.register_callback_query_handler(CustomerCreateTaskLoading.approve_geo_from,
                                         text="approve_geo_from_loading",
                                         state=customer_states.CustomerCreateTaskLoading.geo_position)
    disp.register_message_handler(CustomerCreateTaskLoading.count_man_loading,
                                  state=customer_states.CustomerCreateTaskLoading.people)
    disp.register_message_handler(CustomerCreateTaskLoading.description,
                                  state=customer_states.CustomerCreateTaskLoading.description)
    disp.register_message_handler(CustomerCreateTaskLoading.price,
                                  state=customer_states.CustomerCreateTaskLoading.price)
    disp.register_message_handler(CustomerCreateTaskLoading.expired_order,
                                  state=customer_states.CustomerCreateTaskLoading.expired_data)
    disp.register_message_handler(CustomerCreateTaskLoading.photo_video,
                                  state=customer_states.CustomerCreateTaskLoading.photo_or_video)
    disp.register_message_handler(CustomerCreateTaskLoading.photo,
                                  content_types=['photo', 'text'],
                                  state=customer_states.CustomerCreateTaskLoading.photo)
    disp.register_message_handler(CustomerCreateTaskLoading.video,
                                  content_types=['video', 'text'],
                                  state=customer_states.CustomerCreateTaskLoading.video)
    disp.register_message_handler(CustomerCreateTaskLoading.start_time,
                                  state=customer_states.CustomerCreateTaskLoading.start_time)

    # def register_customer_details_tasks(disp: Dispatcher):
    disp.register_message_handler(CustomerDetailsTasks.customer_details,
                                  state=customer_states.CustomerDetailsTasks.my_tasks)
    disp.register_message_handler(CustomerDetailsTasks.detail_task,
                                  state=customer_states.CustomerDetailsTasks.enter_task,
                                  content_types=['text', 'video_note', 'voice'])
    disp.register_message_handler(CustomerDetailsTasks.detail_task_not_at_work,
                                  state=customer_states.CustomerDetailsTasks.not_at_work)
    disp.register_callback_query_handler(CustomerDetailsTasks.cancel_order_not_at_work,
                                         text='cancel',
                                         state=customer_states.CustomerDetailsTasks.not_at_work)
    disp.register_callback_query_handler(CustomerDetailsTasks.no_cancel_order_not_at_work,
                                         text='no_cancel',
                                         state=customer_states.CustomerDetailsTasks.not_at_work)
    disp.register_callback_query_handler(CustomerDetailsTasks.no_change_order_not_at_work,
                                         text='no_change',
                                         state=["*"])
    disp.register_message_handler(CustomerDetailsTasks.details_task_loading,
                                  state=customer_states.CustomerDetailsTasks.loading,
                                  content_types=['text', 'video_note', 'voice'])
    disp.register_callback_query_handler(CustomerDetailsTasks.close_loading_order,
                                         text="loading_close_order",
                                         state=["*"])
    disp.register_callback_query_handler(CustomerDetailsTasks.no_close_loading_order,
                                         text="loading_no_close",
                                         state=["*"])
    disp.register_callback_query_handler(CustomerDetailsTasks.dismiss_loader,
                                         text="delete_loader",
                                         state=["*"])
    disp.register_callback_query_handler(CustomerDetailsTasks.dismiss_loader_approve,
                                         text_contains="delete_loader_approve_",
                                         state=["*"])

    # def register_customer_details_tasks_change(disp: Dispatcher):
    disp.register_callback_query_handler(CustomerDetailsTasksChange.change_task_enter,
                                         text='change',
                                         state=["*"])
    disp.register_message_handler(CustomerDetailsTasksChange.change_task_main,
                                  state=customer_states.CustomerChangeOrder.enter)
    disp.register_message_handler(CustomerDetailsTasksChange.change_description,
                                  state=customer_states.CustomerChangeOrder.change_description)
    disp.register_message_handler(CustomerDetailsTasksChange.change_money,
                                  state=customer_states.CustomerChangeOrder.change_money)
    disp.register_message_handler(CustomerDetailsTasksChange.change_person,
                                  state=customer_states.CustomerChangeOrder.change_person)
    disp.register_message_handler(CustomerDetailsTasksChange.change_geo,
                                  state=customer_states.CustomerChangeOrder.change_geo,
                                  content_types=['location', 'text', 'web_app_data'])
    disp.register_callback_query_handler(CustomerDetailsTasksChange.change_geo_approve,
                                         text_contains="_change_approve_geo_position_",
                                         state=["*"])
    disp.register_callback_query_handler(CustomerDetailsTasksChange.approve_people_loading,
                                         text="yes_all_people_loading",
                                         state=["*"])
    disp.register_callback_query_handler(CustomerDetailsTasksChange.decline_people_loading,
                                         text="not_all_people_loading",
                                         state=["*"])
    disp.register_callback_query_handler(CustomerDetailsTasksChange.loading_invite_people,
                                         text_contains="loading_invite_",
                                         state=["*"])

    # def register_customer_details_tasks_status(disp: Dispatcher):
    disp.register_message_handler(CustomerDetailsTasksStatus.details_status,
                                  state=customer_states.CustomerDetailsTasksStatus.enter_status)
    disp.register_callback_query_handler(CustomerDetailsTasksStatus.cancel_order,
                                         text="cancel",
                                         state=customer_states.CustomerDetailsTasksStatus.enter_status)
    disp.register_callback_query_handler(CustomerDetailsTasksStatus.no_cancel_order,
                                         text="no_cancel",
                                         state=customer_states.CustomerDetailsTasksStatus.enter_status)
    disp.register_callback_query_handler(CustomerDetailsTasksStatus.close_order,
                                         text="close_order",
                                         state=customer_states.CustomerDetailsTasksStatus.enter_status)
    disp.register_callback_query_handler(CustomerDetailsTasksStatus.no_close,
                                         text="no_close",
                                         state=customer_states.CustomerDetailsTasksStatus.enter_status)
    disp.register_message_handler(CustomerDetailsTasksStatus.rating,
                                  state=customer_states.CustomerDetailsTasksStatus.rating)
    disp.register_message_handler(CustomerDetailsTasksStatus.review,
                                  state=customer_states.CustomerDetailsTasksStatus.review)

    # def register_customer_help(disp: Dispatcher):
    disp.register_message_handler(CustomerHelp.customer_help,
                                  content_types=['text', 'video_note',
                                                 'voice', 'video', 'photo'],
                                  state=customer_states.CustomerHelp.help)

    # def register_customer_history(disp: Dispatcher):
    disp.register_message_handler(CustomerHistory.history,
                                  state=customer_states.CustomerHistory.enter_history)
    disp.register_message_handler(CustomerHistory.order_history,
                                  state=customer_states.CustomerHistory.order_history)
    disp.register_message_handler(CustomerHistory.order_details,
                                  state=customer_states.CustomerHistory.order_history_details)
