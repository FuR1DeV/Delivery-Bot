from aiogram.dispatcher.filters.state import State, StatesGroup


class StoreRegistration(StatesGroup):
    phone: State = State()
    name: State = State()


class StoreStart(StatesGroup):
    store_menu: State = State()

