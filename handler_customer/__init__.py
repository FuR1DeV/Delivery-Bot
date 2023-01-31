__all__ = ["register_customer"]

from aiogram import Dispatcher
from .customer import CustomerMain, CustomerCreateTaskLoading, CustomerCreateTask, CustomerProfile, \
    CustomerCreateTaskComp, CustomerDetailsTasks, CustomerDetailsTasksChange, CustomerDetailsTasksStatus, CustomerHelp,\
    CustomerHistory
from states import customer_states


def register_customer(disp: Dispatcher):
    disp.register_message_handler(CustomerMain.phone, content_types=['contact'],
                                  state=customer_states.CustomerPhone.phone)
    disp.register_callback_query_handler(CustomerMain.hi_customer, text='customer')
    disp.register_message_handler(CustomerMain.main, state=customer_states.CustomerStart.start)
    disp.register_message_handler(CustomerMain.customer_menu, state=customer_states.CustomerStart.customer_menu)
    disp.register_callback_query_handler(CustomerMain.customer_approve, state=["*"], text='customer_yes')
    disp.register_callback_query_handler(CustomerMain.customer_decline, state=["*"], text='customer_no')
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

    # def register_customer_profile(disp: Dispatcher):
    disp.register_message_handler(CustomerProfile.customer_profile,
                                  state=customer_states.CustomerProfile.my_profile)

    # def register_customer_create_task(disp: Dispatcher):
    disp.register_message_handler(CustomerCreateTask.create_task,
                                  state=customer_states.CustomerCreateTask.create)
    disp.register_message_handler(CustomerCreateTask.category_delivery,
                                  state=customer_states.CustomerCreateTask.category_delivery)
    disp.register_message_handler(CustomerCreateTask.geo_position_from,
                                  content_types=['location', 'text'],
                                  state=customer_states.CustomerCreateTask.geo_position_from)
    disp.register_callback_query_handler(CustomerCreateTask.approve_geo_from,
                                         text="approve_geo_from",
                                         state=customer_states.CustomerCreateTask.geo_position_from)
    disp.register_message_handler(CustomerCreateTask.geo_position_to,
                                  content_types=['location', 'text'],
                                  state=customer_states.CustomerCreateTask.geo_position_to)
    disp.register_callback_query_handler(CustomerCreateTask.approve_geo_to,
                                         text="approve_geo_to",
                                         state=customer_states.CustomerCreateTask.geo_position_to)
    disp.register_message_handler(CustomerCreateTask.title,
                                  state=customer_states.CustomerCreateTask.title)
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

    # def register_customer_create_task_comp(disp: Dispatcher):
    disp.register_message_handler(CustomerCreateTaskComp.category_delivery_comp,
                                  state=customer_states.CustomerCreateTaskComp.category_delivery)
    disp.register_message_handler(CustomerCreateTaskComp.geo_position_from_comp,
                                  state=customer_states.CustomerCreateTaskComp.geo_position_from)
    disp.register_callback_query_handler(CustomerCreateTaskComp.approve_geo_from_comp,
                                         text="approve_geo_from_comp",
                                         state=customer_states.CustomerCreateTaskComp.geo_position_from)
    disp.register_message_handler(CustomerCreateTaskComp.geo_position_to_comp,
                                  state=customer_states.CustomerCreateTaskComp.geo_position_to)
    disp.register_callback_query_handler(CustomerCreateTaskComp.approve_geo_to_comp,
                                         text="approve_geo_to_comp",
                                         state=customer_states.CustomerCreateTaskComp.geo_position_to)
    disp.register_message_handler(CustomerCreateTaskComp.title_comp,
                                  state=customer_states.CustomerCreateTaskComp.title)
    disp.register_message_handler(CustomerCreateTaskComp.description_comp,
                                  state=customer_states.CustomerCreateTaskComp.description)
    disp.register_message_handler(CustomerCreateTaskComp.price_comp,
                                  state=customer_states.CustomerCreateTaskComp.price)
    disp.register_message_handler(CustomerCreateTaskComp.performer_category_comp,
                                  state=customer_states.CustomerCreateTaskComp.performer_category)
    disp.register_message_handler(CustomerCreateTaskComp.photo_video_comp,
                                  state=customer_states.CustomerCreateTaskComp.photo_or_video)
    disp.register_message_handler(CustomerCreateTaskComp.photo_comp, content_types=['photo', 'text'],
                                  state=customer_states.CustomerCreateTaskComp.photo)
    disp.register_message_handler(CustomerCreateTaskComp.video_comp, content_types=['video', 'text'],
                                  state=customer_states.CustomerCreateTaskComp.video)
    disp.register_message_handler(CustomerCreateTaskComp.expired_order_comp,
                                  state=customer_states.CustomerCreateTaskComp.expired_data)
    disp.register_message_handler(CustomerCreateTaskComp.order_worth_comp,
                                  state=customer_states.CustomerCreateTaskComp.worth)
    disp.register_message_handler(CustomerCreateTaskComp.choose,
                                  state=customer_states.CustomerCreateTaskComp.choose)
    disp.register_message_handler(CustomerCreateTaskComp.geo_position_from_custom,
                                  state=customer_states.CustomerCreateTaskComp.geo_position_from_custom)
    disp.register_callback_query_handler(CustomerCreateTaskComp.approve_geo_from_custom,
                                         text="approve_geo_from_custom",
                                         state=customer_states.CustomerCreateTaskComp.geo_position_from_custom)
    disp.register_message_handler(CustomerCreateTaskComp.geo_position_to_custom,
                                  state=customer_states.CustomerCreateTaskComp.geo_position_to_custom)
    disp.register_callback_query_handler(CustomerCreateTaskComp.approve_geo_to_custom,
                                         text="approve_geo_to_custom",
                                         state=customer_states.CustomerCreateTaskComp.geo_position_to_custom)

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
                                  state=customer_states.CustomerDetailsTasks.enter_task)
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
                                  state=customer_states.CustomerDetailsTasks.loading)
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
    disp.register_message_handler(CustomerDetailsTasksChange.change,
                                  state=customer_states.CustomerChangeOrder.change)
    disp.register_message_handler(CustomerDetailsTasksChange.change_money,
                                  state=customer_states.CustomerChangeOrder.change_money)
    disp.register_message_handler(CustomerDetailsTasksChange.change_person,
                                  state=customer_states.CustomerChangeOrder.change_person)
    disp.register_message_handler(CustomerDetailsTasksChange.change_geo,
                                  state=customer_states.CustomerChangeOrder.change_geo)
    disp.register_message_handler(CustomerDetailsTasksChange.change_geo_site,
                                  state=customer_states.CustomerChangeOrder.change_geo_site)
    disp.register_callback_query_handler(CustomerDetailsTasksChange.change_geo_site_approve,
                                         state=customer_states.CustomerChangeOrder.change_geo_site,
                                         text="change_geo_position_site")
    disp.register_message_handler(CustomerDetailsTasksChange.change_geo_custom,
                                  state=customer_states.CustomerChangeOrder.change_geo_custom)
    disp.register_callback_query_handler(CustomerDetailsTasksChange.change_geo_custom_approve,
                                         state=customer_states.CustomerChangeOrder.change_geo_custom,
                                         text="change_geo_position_custom")
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
                                  content_types=['text'],
                                  state=customer_states.CustomerHelp.help)
    disp.register_message_handler(CustomerHelp.customer_upload_photo,
                                  content_types=['photo', 'text'],
                                  state=customer_states.CustomerHelp.upload_photo)
    disp.register_message_handler(CustomerHelp.customer_upload_video,
                                  content_types=['video', 'text'],
                                  state=customer_states.CustomerHelp.upload_video)

    # def register_customer_history(disp: Dispatcher):
    disp.register_message_handler(CustomerHistory.history,
                                  state=customer_states.CustomerHistory.enter_history)
    disp.register_message_handler(CustomerHistory.order_history,
                                  state=customer_states.CustomerHistory.order_history)
    disp.register_message_handler(CustomerHistory.order_details,
                                  state=customer_states.CustomerHistory.order_history_details)
