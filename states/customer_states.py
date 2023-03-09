from aiogram.dispatcher.filters.state import State, StatesGroup


class CustomerPhone(StatesGroup):
    phone: State = State()


class CustomerStart(StatesGroup):
    start: State = State()
    customer_menu: State = State()
    proposal: State = State()
    orders: State = State()


class CustomerCreateTask(StatesGroup):
    category_delivery: State = State()
    geo_position_from: State = State()
    geo_position_to: State = State()
    description: State = State()
    price: State = State()
    performer_category: State = State()
    expired_data: State = State()
    worth: State = State()
    photo_or_video: State = State()
    photo: State = State()
    video: State = State()


class CustomerCreateTaskLoading(StatesGroup):
    geo_position: State = State()
    people: State = State()
    description: State = State()
    price: State = State()
    start_time: State = State()
    expired_data: State = State()
    photo_or_video: State = State()
    photo: State = State()
    video: State = State()


class CustomerProfile(StatesGroup):
    my_profile: State = State()
    balance: State = State()
    my_performer: State = State()


class CustomerDetailsTasks(StatesGroup):
    my_tasks: State = State()
    enter_task: State = State()
    not_at_work: State = State()
    loading: State = State()


class CustomerDetailsTasksStatus(StatesGroup):
    enter_status: State = State()
    rating: State = State()
    review: State = State()


class CustomerHistory(StatesGroup):
    enter_history: State = State()
    order_history: State = State()
    order_history_details: State = State()


class CustomerHelp(StatesGroup):
    help: State = State()
    upload_photo: State = State()
    upload_video: State = State()


class CustomerChangeOrder(StatesGroup):
    enter: State = State()
    change_description: State = State()
    change_money: State = State()
    change_geo: State = State()
    change_person: State = State()
