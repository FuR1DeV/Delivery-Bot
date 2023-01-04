from aiogram.dispatcher.filters.state import State, StatesGroup


class PerformerPhone(StatesGroup):
    phone: State = State()


class PerformerHistory(StatesGroup):
    enter_history: State = State()
    order_history: State = State()
    order_history_details: State = State()


class PerformerStart(StatesGroup):
    start: State = State()
    performer_menu: State = State()


class PerformerProfile(StatesGroup):
    my_profile: State = State()
    balance: State = State()
    change_status: State = State()
    change_status_transport: State = State()
    pay: State = State()


class PerformerDetailsTasks(StatesGroup):
    details_tasks: State = State()
    enter_task: State = State()


class PerformerCompetedTasks(StatesGroup):
    completed_tasks: State = State()


class PerformerHelp(StatesGroup):
    help: State = State()
    upload_photo: State = State()
    upload_video: State = State()


class PerformerTasks(StatesGroup):
    check_all_orders: State = State()
    get_order: State = State()
    approve_or_decline: State = State()
    proposal: State = State()


class PerformerDetailsTasksStatus(StatesGroup):
    enter_status: State = State()
    rating: State = State()
    review: State = State()
