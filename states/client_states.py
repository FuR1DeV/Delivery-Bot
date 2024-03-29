from aiogram.dispatcher.filters.state import State, StatesGroup


class ClientRegistration(StatesGroup):
    phone: State = State()
    name: State = State()


class ClientClear(StatesGroup):
    client_clear: State = State()


class ClientCreateOrder(StatesGroup):
    create_order_text: State = State()
    create_order_photo: State = State()
