__all__ = ["register_client"]

from aiogram import Dispatcher
from handler_client.client_1 import ClientMain
from handler_client.client_2 import ClientCreateOrder
from states import client_states


def register_client(disp: Dispatcher):

    """Client Clear"""
    disp.register_message_handler(ClientMain.client_clear,
                                  state=client_states.ClientClear.client_clear)

    """Client Main"""
    disp.register_callback_query_handler(ClientMain.hi_client,
                                         text='client')
    disp.register_message_handler(ClientMain.client_phone,
                                  content_types=['contact', 'text'],
                                  state=client_states.ClientRegistration.phone)
    disp.register_callback_query_handler(ClientMain.client_start,
                                         text="start_client",
                                         state=["*"])
    disp.register_callback_query_handler(ClientMain.client_menu,
                                         text="client_main_menu",
                                         state=["*"])
    disp.register_callback_query_handler(ClientMain.client_profile,
                                         text="client_profile",
                                         state=["*"])

    """Client Create Order"""
    disp.register_callback_query_handler(ClientCreateOrder.client_create_order,
                                         text="client_create_order",
                                         state=["*"])
    disp.register_message_handler(ClientCreateOrder.client_create_order_text,
                                  content_types=['photo', 'text'],
                                  state=client_states.ClientCreateOrder.create_order_text)
    disp.register_callback_query_handler(ClientCreateOrder.client_create_order_photo,
                                         text="client_create_order_photo",
                                         state=["*"])
    disp.register_message_handler(ClientCreateOrder.client_create_order_photo_add,
                                  content_types=['photo', 'text'],
                                  state=client_states.ClientCreateOrder.create_order_photo)
    disp.register_callback_query_handler(ClientCreateOrder.client_create_order_finish,
                                         text="client_create_order_finish",
                                         state=["*"])
