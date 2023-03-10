__all__ = ["register_store"]

from aiogram import Dispatcher
from handler_store.store_1 import StoreMain
from states import store_states


def register_store(disp: Dispatcher):
    disp.register_callback_query_handler(StoreMain.hi_store,
                                         text='store')
    disp.register_message_handler(StoreMain.store_phone,
                                  content_types=['contact', 'text'],
                                  state=store_states.StoreRegistration.phone)
    disp.register_message_handler(StoreMain.store_name,
                                  content_types=['contact', 'text'],
                                  state=store_states.StoreRegistration.name)
    disp.register_callback_query_handler(StoreMain.store_start,
                                         text="start_store",
                                         state=["*"])
