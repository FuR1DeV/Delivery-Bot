from aiogram.dispatcher.filters.state import State, StatesGroup


class AdminStates(StatesGroup):
    enter: State = State()
    loading_db: State = State()
    orders: State = State()
    jobs: State = State()
    control: State = State()


class Orders(StatesGroup):
    enter: State = State()
    order: State = State()
    detail_order: State = State()


class Commission(StatesGroup):
    commission: State = State()
    commission_set: State = State()
    commission_promo: State = State()
    commission_promo_find_id: State = State()
    commission_promo_set_discount: State = State()
    commission_for_performer: State = State()
    commission_for_customer: State = State()


class CommissionForCategories(StatesGroup):
    commission_for_categories: State = State()
    commission_for_category: State = State()


class AboutUsers(StatesGroup):
    enter: State = State()
    find_id: State = State()
    find_first_name: State = State()
    find_username: State = State()
    find_telephone: State = State()


class ChangeUsers(StatesGroup):
    enter: State = State()
    add_money: State = State()
    change_first_name: State = State()
    change_last_name: State = State()
    rating: State = State()


class Statistics(StatesGroup):
    enter: State = State()


class Advert(StatesGroup):
    enter: State = State()
