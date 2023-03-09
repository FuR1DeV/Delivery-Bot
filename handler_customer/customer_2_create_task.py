from random import randint
from datetime import datetime, timedelta
from aiogram import types
from aiogram.dispatcher import FSMContext
from geopy import distance
from geopy.geocoders import Nominatim

from bot import bot
from data.commands import customers_get, customers_set, general_set, general_get
from markups import markup_customer, markup_performer
from states import customer_states
from settings import config
from settings.config import KEYBOARD


class CustomerCreateTask:

    @staticmethod
    async def category_delivery(message: types.Message, state: FSMContext):
        category = [f"{KEYBOARD.get('BOUQUET')} Цветы",
                    f"{KEYBOARD.get('WRAPPED_GIFT')} Подарки",
                    f"{KEYBOARD.get('SHORTCAKE')} Кондитерка",
                    f"{KEYBOARD.get('PAGE_WITH_WITH_CURL')} Документы",
                    f"{KEYBOARD.get('ARROWS_BUTTON')} Погрузка/Разгрузка",
                    f"{KEYBOARD.get('INPUT_LATIN_LETTERS')} Другое"]
        if message.text in category:
            await bot.send_message(message.from_user.id,
                                   f"Отлично! Вы выбрали категорию {message.text}")
            async with state.proxy() as data:
                data["category_delivery"] = message.text.split()[1]
            if message.text == f"{KEYBOARD.get('ARROWS_BUTTON')} Погрузка/Разгрузка":
                await bot.send_message(message.from_user.id,
                                       "<b>Куда выезжать ?</b>\n"
                                       "Справа <b>скрепка</b> нажмите на неё, далее внизу будет выбор "
                                       "Галерея, Файл, <b>Геопозиция</b>, Опрос.\n"
                                       "Выберите Геопозиция и далее можете искать конечную точку на карте\n"
                                       "ИЛИ можете ввести адрес вручную ГОРОД УЛИЦА ДОМ\n"
                                       "ПРИМЕР:\n"
                                       "Москва Лобачевского 12",
                                       reply_markup=markup_customer.send_my_geo())
                await customer_states.CustomerCreateTaskLoading.geo_position.set()
            else:
                await bot.send_message(message.from_user.id,
                                       "<b>Точка А</b>\n"
                                       "У вас есть 3 варианта отправки Адреса\n"
                                       "<b>1.</b> Через ввод адреса с всплывающим меню и "
                                       "отправкой через Адреса кнопку Отправить\n"
                                       "<b>2.</b> Справа <b>СКРЕПКА</b> нажмите на неё, далее внизу будет выбор "
                                       "Галерея, Файл, <b>Геопозиция</b>, Опрос.\n"
                                       "Выберите Геопозиция и далее можете искать точку на карте\n"
                                       "<b>3.</b> Ввести адрес вручную ГОРОД УЛИЦА ДОМ\n"
                                       "ПРИМЕР:\n"
                                       "Москва Лобачевского 12",
                                       reply_markup=markup_customer.send_my_geo())
                await customer_states.CustomerCreateTask.next()
        if message.text == f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Вернуться в главное меню":
            await customer_states.CustomerStart.customer_menu.set()
            not_at_work = await customers_get.customer_all_orders_not_at_work(message.from_user.id)
            at_work = await customers_get.customer_all_orders_in_work(message.from_user.id)
            loading = await customers_get.customer_all_orders_loading(message.from_user.id)
            await bot.send_message(message.from_user.id,
                                   f"{markup_customer.text_menu(len(not_at_work), len(at_work), len(loading))}",
                                   reply_markup=markup_customer.main_menu())

    @staticmethod
    async def geo_position_from(message: types.Message, state: FSMContext):
        if message.location:
            try:
                n = Nominatim(user_agent=f'FlowWork_{message.from_user.id}')
                loc = f"{message.location.latitude}, {message.location.longitude}"
                address = n.reverse(loc)
                city = address.raw.get("address").get("city")
                if city is None:
                    city = address.raw.get("address").get("town")
                await bot.send_message(message.from_user.id,
                                       f'Город подачи: {city}\n'
                                       f'Адрес подачи: {address.raw.get("address").get("road")}, '
                                       f'{address.raw.get("address").get("house_number")}\n')
                await bot.send_message(message.from_user.id,
                                       "Проверьте пожалуйста координаты, если вы ошиблись "
                                       "вы можете еще раз отправить геопозицию.\n"
                                       "Если же все в порядке нажмите <b>Все верно</b>",
                                       reply_markup=markup_customer.inline_approve_geo_from())
                async with state.proxy() as data:
                    data["geo_data_from"] = f'{city}, ' \
                                            f'{address.raw.get("address").get("road")}, ' \
                                            f'{address.raw.get("address").get("house_number")}'
            except AttributeError:
                pass
        if message.text:
            if message.text == f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад":
                await customer_states.CustomerCreateTask.category_delivery.set()
                await bot.send_message(message.from_user.id,
                                       "Вы вернулись на шаг назад\n"
                                       "Здесь вы можете выбрать <b>категорию Заказа</b>",
                                       reply_markup=markup_customer.category_delivery())
            if message.text != f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад":
                msg = message.text.split()
                if len(msg) == 4:
                    await bot.send_message(message.from_user.id,
                                           f'Город подачи: {msg[0]}\n'
                                           f'Адрес подачи: {msg[1]} {msg[2]} - '
                                           f'{msg[-1]}')
                    await bot.send_message(message.from_user.id,
                                           "Проверьте пожалуйста введенные данные, если вы ошиблись "
                                           "вы можете еще раз отправить адрес.\n"
                                           "Если же все в порядке нажмите Все верно",
                                           reply_markup=markup_customer.inline_approve_geo_from())
                    async with state.proxy() as data:
                        data["geo_data_from"] = message.text
                elif len(msg) == 3:
                    await bot.send_message(message.from_user.id,
                                           f'Город подачи: {msg[0]}\n'
                                           f'Адрес подачи: {msg[1]} - '
                                           f'{msg[-1]}')
                    await bot.send_message(message.from_user.id,
                                           "Проверьте пожалуйста введенные данные, если вы ошиблись "
                                           "вы можете еще раз отправить адрес.\n"
                                           "Если же все в порядке нажмите Все верно",
                                           reply_markup=markup_customer.inline_approve_geo_from())
                    async with state.proxy() as data:
                        data["geo_data_from"] = message.text
                else:
                    await bot.send_message(message.from_user.id,
                                           "Надо ввести данные в формате\n"
                                           "<b>Город Улица Дом</b>")
        if message.web_app_data:
            address = message.web_app_data.data
            await bot.send_message(message.from_user.id,
                                   f'Адрес который вы ввели - {address}')
            await bot.send_message(message.from_user.id,
                                   "Проверьте пожалуйста Адрес, если вы ошиблись "
                                   "вы можете еще раз отправить Адрес через Ввод Адреса.\n"
                                   "Если же все в порядке нажмите <b>Все верно</b>",
                                   reply_markup=markup_customer.inline_approve_geo_from())
            async with state.proxy() as data:
                data["geo_data_from"] = address

    @staticmethod
    async def approve_geo_from(callback: types.CallbackQuery):
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        await bot.send_message(callback.from_user.id,
                               "<b>Точка B</b>\n"
                               "У вас есть 3 варианта отправки Адреса\n"
                               "<b>1.</b> Через ввод адреса с всплывающим меню и "
                               "отправкой через Адреса кнопку Отправить\n"
                               "<b>2.</b> Справа <b>СКРЕПКА</b> нажмите на неё, далее внизу будет выбор "
                               "Галерея, Файл, <b>Геопозиция</b>, Опрос.\n"
                               "Выберите Геопозиция и далее можете искать точку на карте\n"
                               "<b>3.</b> Ввести адрес вручную ГОРОД УЛИЦА ДОМ\n"
                               "ПРИМЕР:\n"
                               "Москва Лобачевского 12",
                               reply_markup=markup_customer.send_my_geo_2())
        await customer_states.CustomerCreateTask.geo_position_to.set()

    @staticmethod
    async def geo_position_to(message: types.Message, state: FSMContext):
        if message.location:
            try:
                n = Nominatim(user_agent=f'FlowWork_{message.from_user.id}')
                loc = f"{message.location.latitude}, {message.location.longitude}"
                address = n.reverse(loc)
                city = address.raw.get("address").get("city")
                if city is None:
                    city = address.raw.get("address").get("town")
                await bot.send_message(message.from_user.id,
                                       f'Город доставки: {city}\n'
                                       f'Адрес доставки: {address.raw.get("address").get("road")}, '
                                       f'{address.raw.get("address").get("house_number")}\n')
                await bot.send_message(message.from_user.id,
                                       "Проверьте пожалуйста координаты, если вы ошиблись "
                                       "вы можете еще раз отправить геопозицию. "
                                       "Если же все в порядке нажмите Все верно",
                                       reply_markup=markup_customer.inline_approve_geo_to())
                async with state.proxy() as data:
                    data["geo_data_to"] = f'{city}, ' \
                                          f'{address.raw.get("address").get("road")}, ' \
                                          f'{address.raw.get("address").get("house_number")}'
            except AttributeError:
                pass
        if message.text:
            if message.text == f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад":
                await customer_states.CustomerCreateTask.geo_position_from.set()
                await bot.send_message(message.from_user.id,
                                       "Вы вернулись на шаг назад\n"
                                       "Здесь вы можете указать <b>Точку А</b> (Откуда забрать)",
                                       reply_markup=markup_customer.send_my_geo())
            if message.text != f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад":
                msg = message.text.split()
                if len(msg) == 4:
                    await bot.send_message(message.from_user.id,
                                           f'Город подачи: {msg[0]}\n'
                                           f'Адрес подачи: {msg[1]} {msg[2]} - '
                                           f'{msg[-1]}')
                    await bot.send_message(message.from_user.id,
                                           "Проверьте пожалуйста введенные данные, если вы ошиблись "
                                           "вы можете еще раз отправить адрес.\n"
                                           "Если же все в порядке нажмите Все верно",
                                           reply_markup=markup_customer.inline_approve_geo_to())
                    async with state.proxy() as data:
                        data["geo_data_to"] = message.text
                elif len(msg) == 3:
                    await bot.send_message(message.from_user.id,
                                           f'Город подачи: {msg[0]}\n'
                                           f'Адрес подачи: {msg[1]} - '
                                           f'{msg[-1]}')
                    await bot.send_message(message.from_user.id,
                                           "Проверьте пожалуйста введенные данные, если вы ошиблись "
                                           "вы можете еще раз отправить адрес.\n"
                                           "Если же все в порядке нажмите Все верно",
                                           reply_markup=markup_customer.inline_approve_geo_to())
                    async with state.proxy() as data:
                        data["geo_data_to"] = message.text
                else:
                    await bot.send_message(message.from_user.id,
                                           "Надо ввести данные в формате\n"
                                           "<b>Город Улица Дом</b>")
        if message.web_app_data:
            address = message.web_app_data.data
            await bot.send_message(message.from_user.id,
                                   f'Адрес который вы ввели - {address}')
            await bot.send_message(message.from_user.id,
                                   "Проверьте пожалуйста Адрес, если вы ошиблись "
                                   "вы можете еще раз отправить Адрес через Ввод Адреса.\n"
                                   "Если же все в порядке нажмите <b>Все верно</b>",
                                   reply_markup=markup_customer.inline_approve_geo_to())
            async with state.proxy() as data:
                data["geo_data_to"] = address

    @staticmethod
    async def approve_geo_to(callback: types.CallbackQuery):
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        await bot.send_message(callback.from_user.id,
                               "Отлично! Опишите что нужно сделать",
                               reply_markup=markup_customer.back())
        await customer_states.CustomerCreateTask.description.set()

    @staticmethod
    async def description(message: types.Message, state: FSMContext):
        if message.text == f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад":
            await customer_states.CustomerCreateTask.geo_position_to.set()
            await bot.send_message(message.from_user.id,
                                   "Вы вернулись на шаг назад\n"
                                   "Здесь вы можете указать <b>Точку B</b> (Конечная точка)",
                                   reply_markup=markup_customer.send_my_geo_2())
        else:
            if len(message.text) > 255:
                await bot.send_message(message.from_user.id,
                                       "Вы ввели слишком длинное описание!"
                                       "Ограничение в описании заказа 255 символов!",
                                       reply_markup=markup_customer.back())
            else:
                async with state.proxy() as data:
                    data["description"] = message.text
                await customer_states.CustomerCreateTask.next()
                await bot.send_message(message.from_user.id,
                                       "Предложите цену исполнителю",
                                       reply_markup=markup_customer.back())

    @staticmethod
    async def price(message: types.Message, state: FSMContext):
        if message.text == f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад":
            await customer_states.CustomerCreateTask.description.set()
            await bot.send_message(message.from_user.id,
                                   "Вы вернулись на шаг назад\n"
                                   "Здесь вы сможете ввести <b>описание Заказа</b>",
                                   reply_markup=markup_customer.back())
        if message.text.isdigit():
            async with state.proxy() as data:
                data["price"] = message.text
            await bot.send_message(message.from_user.id,
                                   "Выберите категорию Исполнителя",
                                   reply_markup=markup_customer.performer_category())
            await customer_states.CustomerCreateTask.next()
        elif message.text != f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад":
            await bot.send_message(message.from_user.id,
                                   "Надо ввести целое число")

    @staticmethod
    async def performer_category(message: types.Message, state: FSMContext):
        if "На машине" in message.text:
            async with state.proxy() as data:
                data['performer_category'] = "car"
            await bot.send_message(message.from_user.id,
                                   "<b>Сколько часов максимум актуален ваш заказ ?</b>",
                                   reply_markup=markup_customer.back())
            await customer_states.CustomerCreateTask.next()
        if "На скутере" in message.text:
            async with state.proxy() as data:
                data['performer_category'] = "scooter"
            await bot.send_message(message.from_user.id,
                                   "<b>Сколько часов максимум актуален ваш заказ ?</b>",
                                   reply_markup=markup_customer.back())
            await customer_states.CustomerCreateTask.next()
        if "Пешеход" in message.text:
            async with state.proxy() as data:
                data['performer_category'] = "pedestrian"
            await bot.send_message(message.from_user.id,
                                   "<b>Сколько часов максимум актуален ваш заказ ?</b>",
                                   reply_markup=markup_customer.back())
            await customer_states.CustomerCreateTask.next()
        if "Любой" in message.text:
            async with state.proxy() as data:
                data['performer_category'] = "any"
            await bot.send_message(message.from_user.id,
                                   "<b>Сколько часов максимум актуален ваш заказ ?</b>",
                                   reply_markup=markup_customer.back())
            await customer_states.CustomerCreateTask.next()
        if message.text == f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад":
            await customer_states.CustomerCreateTask.price.set()
            await bot.send_message(message.from_user.id,
                                   "Вы вернулись на шаг назад\n"
                                   "Здесь вы сможете ввести <b>цену Заказа</b>",
                                   reply_markup=markup_customer.back())

    @staticmethod
    async def expired_order(message: types.Message, state: FSMContext):
        if message.text == f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад":
            await customer_states.CustomerCreateTask.performer_category.set()
            await bot.send_message(message.from_user.id,
                                   "Вы вернулись на шаг назад\n"
                                   "Здесь вы сможете выбрать желаемую <b>категорию Исполнителя</b>",
                                   reply_markup=markup_customer.performer_category())
        if message.text.isdigit():
            if 1 <= int(message.text) <= 12:
                date = datetime.now() + timedelta(hours=int(message.text))
                await bot.send_message(message.from_user.id,
                                       f"Ваш заказ действует <b>{message.text} часа</b>\n"
                                       f"До {date.strftime('%d %B %Y, %H:%M')}\n"
                                       f"Если по истечении этого времени никто ваш заказ не возьмет\n"
                                       f"Заказ исчезнет автоматически")
                async with state.proxy() as data:
                    data['order_expired'] = date
                await bot.send_message(message.from_user.id,
                                       "<b>Определите примерную ценность вашего товара</b>\n"
                                       "<b>Если ценности нет, напишите 0</b>\n",
                                       reply_markup=markup_customer.back())
                await customer_states.CustomerCreateTask.next()
            else:
                await bot.send_message(message.from_user.id,
                                       f"Введите от 1 до 12 часов")
        if message.text != f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад" \
                and not message.text.isdigit():
            await bot.send_message(message.from_user.id,
                                   "Нужно ввести цифру\n"
                                   "Введите сколько часов действует ваш заказ")

    @staticmethod
    async def order_worth(message: types.Message, state: FSMContext):
        if message.text == f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад":
            await customer_states.CustomerCreateTask.expired_data.set()
            await bot.send_message(message.from_user.id,
                                   "Вы вернулись на шаг назад\n"
                                   "Здесь вы сможете определить <b>срок истечения вашего Заказа</b>",
                                   reply_markup=markup_customer.back())
        if message.text.isdigit() and int(message.text) < 15001:
            await bot.send_message(message.from_user.id,
                                   f"Вы определили ценность вашего товара <b>{message.text} руб.</b>")
            async with state.proxy() as data:
                data['order_worth'] = message.text
            await bot.send_message(message.from_user.id,
                                   "Загрузите фото или видео",
                                   reply_markup=markup_customer.photo_or_video_create_task())
            await customer_states.CustomerCreateTask.next()
        if message.text.isdigit() and int(message.text) > 15000:
            await bot.send_message(message.from_user.id,
                                   "Максимальная ценность товара в 15000 рублей\n"
                                   "Определите примерную ценность вашего товара")
        elif message.text != f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад" and not message.text.isdigit():
            await bot.send_message(message.from_user.id,
                                   "Нужно ввести цифру\n"
                                   "Определите примерную ценность вашего товара")

    @staticmethod
    async def photo_video(message: types.Message, state: FSMContext):
        order_id = f"{datetime.now().strftime('%m_%d')}_{randint(1, 99999)}"
        geolocator = Nominatim(user_agent=f'FlowWork_{message.from_user.id}')
        async with state.proxy() as data:
            data["order_id"] = order_id
        if message.text == "Без фото или видео":
            await bot.send_message(message.from_user.id,
                                   "Подождите немножко, размещаем ваш заказ")
            async with state.proxy() as data:
                await customers_set.customer_add_order(message.from_user.id,
                                                       data.get("geo_data_from"),
                                                       data.get("geo_data_to"),
                                                       int(data.get("price")),
                                                       data.get("description"),
                                                       None, None,
                                                       order_id,
                                                       datetime.now().strftime('%d-%m-%Y, %H:%M:%S'),
                                                       data.get("category_delivery"),
                                                       data.get("performer_category"),
                                                       data.get("order_expired").strftime('%d-%m-%Y, %H:%M:%S'),
                                                       int(data.get("order_worth")))
            await general_set.add_review(order_id)
            performers = await general_get.all_performers_auto_send(data.get("performer_category"))
            if performers:
                for i in performers:
                    try:
                        loc_a = geolocator.geocode(data.get("geo_data_from"))
                        loc_a = loc_a.latitude, loc_a.longitude
                        location_result = f"{round(distance.distance(loc_a, i.geo_position).km, 2)} км"
                    except AttributeError:
                        location_result = f"Не получилось определить {config.KEYBOARD.get('FROWNING_FACE')}"
                    await bot.send_message(i.user_id,
                                           "Новый заказ!\n"
                                           f"{config.KEYBOARD.get('DASH') * 14}\n"
                                           f"{config.KEYBOARD.get('INPUT_LATIN_LETTERS')} "
                                           f"Категория - <b>{data.get('category_delivery')}</b>\n"
                                           f"{config.KEYBOARD.get('A_BUTTON')} "
                                           f"Откуда - <a href='https://yandex.ru/maps/?text="
                                           f"{'+'.join(data.get('geo_data_from').split())}'>"
                                           f"{data.get('geo_data_from')}</a>\n"
                                           f"{config.KEYBOARD.get('B_BUTTON')} "
                                           f"Куда - <a href='https://yandex.ru/maps/?text="
                                           f"{'+'.join(data.get('geo_data_to').split())}'>"
                                           f"{data.get('geo_data_to')}</a>\n"
                                           f"{config.KEYBOARD.get('CLIPBOARD')} "
                                           f"Описание - <b>{data.get('description')}</b>\n"
                                           f"{config.KEYBOARD.get('DOLLAR')} "
                                           f"Цена - <b>{data.get('price')}</b>\n"
                                           f"{config.KEYBOARD.get('MONEY_BAG')} "
                                           f"Ценность товара - <b>{data.get('order_worth')}</b>\n"
                                           f"{config.KEYBOARD.get('WORLD_MAP')} "
                                           f"Точка <b>А</b> находится в радиусе: "
                                           f"<b>{location_result}</b>\n"
                                           f"{config.KEYBOARD.get('DASH') * 14}",
                                           disable_web_page_preview=True)
            await customer_states.CustomerStart.customer_menu.set()
            await bot.send_message(message.from_user.id,
                                   "<b>Отклик без фото или видео отправлен.</b>\n"
                                   "<b>Ожидайте пока Исполнитель примет ваш заказ!</b>")
            not_at_work = await customers_get.customer_all_orders_not_at_work(message.from_user.id)
            at_work = await customers_get.customer_all_orders_in_work(message.from_user.id)
            loading = await customers_get.customer_all_orders_loading(message.from_user.id)
            await bot.send_message(message.from_user.id,
                                   f"{markup_customer.text_menu(len(not_at_work), len(at_work), len(loading))}",
                                   reply_markup=markup_customer.main_menu())
        if message.text == "Загрузить Фото":
            await customer_states.CustomerCreateTask.photo.set()
            await bot.send_message(message.from_user.id,
                                   f"{message.from_user.first_name} Загрузите фото",
                                   reply_markup=markup_customer.back())
        if message.text == "Загрузить Видео":
            await customer_states.CustomerCreateTask.video.set()
            await bot.send_message(message.from_user.id,
                                   f"{message.from_user.first_name} Загрузите видео",
                                   reply_markup=markup_customer.back())
        if message.text == f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад":
            await customer_states.CustomerCreateTask.worth.set()
            await bot.send_message(message.from_user.id,
                                   "Вы вернулись на шаг назад\n"
                                   "Здесь вы сможете выбрать определить <b>ценность вашего товара</b>",
                                   reply_markup=markup_customer.back())

    @staticmethod
    async def photo(message: types.Message, state: FSMContext):
        if message.text == f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад":
            await customer_states.CustomerCreateTask.photo_or_video.set()
            await bot.send_message(message.from_user.id,
                                   "Вы вернулись на шаг назад\n"
                                   "Здесь вы сможете выбрать загрузку с Фото или Видео\n"
                                   "Или можно Без Фото и Видео",
                                   reply_markup=markup_customer.photo_or_video_create_task())
        else:
            try:
                async with state.proxy() as data:
                    data["photo"] = message.photo[2].file_id
                await bot.send_message(message.from_user.id,
                                       "Подождите немножко, размещаем ваш заказ")
                geolocator = Nominatim(user_agent=f'FlowWork_{message.from_user.id}')
                await customers_set.customer_add_order(message.from_user.id,
                                                       data.get("geo_data_from"),
                                                       data.get("geo_data_to"),
                                                       int(data.get("price")),
                                                       data.get("description"),
                                                       data.get("photo"), None,
                                                       data.get("order_id"),
                                                       datetime.now().strftime('%d-%m-%Y, %H:%M:%S'),
                                                       data.get("category_delivery"),
                                                       data.get("performer_category"),
                                                       data.get("order_expired").strftime('%d-%m-%Y, %H:%M:%S'),
                                                       int(data.get("order_worth")))
                await general_set.add_review(data.get("order_id"))
                performers = await general_get.all_performers_auto_send(data.get("performer_category"))
                if performers:
                    for i in performers:
                        try:
                            loc_a = geolocator.geocode(data.get("geo_data_from"))
                            loc_a = loc_a.latitude, loc_a.longitude
                            location_result = f"{round(distance.distance(loc_a, i.geo_position).km, 2)} км"
                        except AttributeError:
                            location_result = f"Не получилось определить {config.KEYBOARD.get('FROWNING_FACE')}"
                        await bot.send_message(i.user_id,
                                               "Новый заказ!\n"
                                               f"{config.KEYBOARD.get('DASH') * 14}\n"
                                               f"{config.KEYBOARD.get('INPUT_LATIN_LETTERS')} "
                                               f"Категория - <b>{data.get('category_delivery')}</b>\n"
                                               f"{config.KEYBOARD.get('A_BUTTON')} "
                                               f"Откуда - <a href='https://yandex.ru/maps/?text="
                                               f"{'+'.join(data.get('geo_data_from').split())}'>"
                                               f"{data.get('geo_data_from')}</a>\n"
                                               f"{config.KEYBOARD.get('B_BUTTON')} "
                                               f"Куда - <a href='https://yandex.ru/maps/?text="
                                               f"{'+'.join(data.get('geo_data_to').split())}'>"
                                               f"{data.get('geo_data_to')}</a>\n"
                                               f"{config.KEYBOARD.get('CLIPBOARD')} "
                                               f"Описание - <b>{data.get('description')}</b>\n"
                                               f"{config.KEYBOARD.get('DOLLAR')} "
                                               f"Цена - <b>{data.get('price')}</b>\n"
                                               f"{config.KEYBOARD.get('MONEY_BAG')} "
                                               f"Ценность товара - <b>{data.get('order_worth')}</b>\n"
                                               f"{config.KEYBOARD.get('WORLD_MAP')} "
                                               f"Точка <b>А</b> находится в радиусе: "
                                               f"<b>{location_result}</b>\n"
                                               f"{config.KEYBOARD.get('DASH') * 14}",
                                               disable_web_page_preview=True)
                await customer_states.CustomerStart.customer_menu.set()
                await bot.send_message(message.from_user.id,
                                       "<b>Отклик с фото отправлен.</b>\n"
                                       "<b>Ожидайте пока Исполнитель примет ваш заказ!</b>")
                not_at_work = await customers_get.customer_all_orders_not_at_work(message.from_user.id)
                at_work = await customers_get.customer_all_orders_in_work(message.from_user.id)
                loading = await customers_get.customer_all_orders_loading(message.from_user.id)
                await bot.send_message(message.from_user.id,
                                       f"{markup_customer.text_menu(len(not_at_work), len(at_work), len(loading))}",
                                       reply_markup=markup_customer.main_menu())
            except IndexError:
                pass

    @staticmethod
    async def video(message: types.Message, state: FSMContext):
        if message.text == f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад":
            await customer_states.CustomerCreateTask.photo_or_video.set()
            await bot.send_message(message.from_user.id,
                                   "Вы вернулись на шаг назад\n"
                                   "Здесь вы сможете выбрать загрузку с Фото или Видео\n"
                                   "Или можно Без Фото и Видео",
                                   reply_markup=markup_customer.photo_or_video_create_task())
        else:
            async with state.proxy() as data:
                data["video"] = message.video.file_id
            await bot.send_message(message.from_user.id,
                                   "Подождите немножко, размещаем ваш заказ")
            geolocator = Nominatim(user_agent=f'FlowWork_{message.from_user.id}')
            await customers_set.customer_add_order(message.from_user.id,
                                                   data.get("geo_data_from"),
                                                   data.get("geo_data_to"),
                                                   int(data.get("price")),
                                                   data.get("description"),
                                                   None, data.get("video"),
                                                   data.get("order_id"),
                                                   datetime.now().strftime('%d-%m-%Y, %H:%M:%S'),
                                                   data.get("category_delivery"),
                                                   data.get("performer_category"),
                                                   data.get("order_expired").strftime('%d-%m-%Y, %H:%M:%S'),
                                                   int(data.get("order_worth")))
            await general_set.add_review(data.get("order_id"))
            performers = await general_get.all_performers_auto_send(data.get("performer_category"))
            if performers:
                for i in performers:
                    try:
                        loc_a = geolocator.geocode(data.get("geo_data_from"))
                        loc_a = loc_a.latitude, loc_a.longitude
                        location_result = f"{round(distance.distance(loc_a, i.geo_position).km, 2)} км"
                    except AttributeError:
                        location_result = f"Не получилось определить {config.KEYBOARD.get('FROWNING_FACE')}"
                    await bot.send_message(i.user_id,
                                           "Новый заказ!\n"
                                           f"{config.KEYBOARD.get('DASH') * 14}\n"
                                           f"{config.KEYBOARD.get('INPUT_LATIN_LETTERS')} "
                                           f"Категория - <b>{data.get('category_delivery')}</b>\n"
                                           f"{config.KEYBOARD.get('A_BUTTON')} "
                                           f"Откуда - <a href='https://yandex.ru/maps/?text="
                                           f"{'+'.join(data.get('geo_data_from').split())}'>"
                                           f"{data.get('geo_data_from')}</a>\n"
                                           f"{config.KEYBOARD.get('B_BUTTON')} "
                                           f"Куда - <a href='https://yandex.ru/maps/?text="
                                           f"{'+'.join(data.get('geo_data_to').split())}'>"
                                           f"{data.get('geo_data_to')}</a>\n"
                                           f"{config.KEYBOARD.get('CLIPBOARD')} "
                                           f"Описание - <b>{data.get('description')}</b>\n"
                                           f"{config.KEYBOARD.get('DOLLAR')} "
                                           f"Цена - <b>{data.get('price')}</b>\n"
                                           f"{config.KEYBOARD.get('MONEY_BAG')} "
                                           f"Ценность товара - <b>{data.get('order_worth')}</b>\n"
                                           f"{config.KEYBOARD.get('WORLD_MAP')} "
                                           f"Точка <b>А</b> находится в радиусе: "
                                           f"<b>{location_result}</b>\n"
                                           f"{config.KEYBOARD.get('DASH') * 14}",
                                           disable_web_page_preview=True)
            await customer_states.CustomerStart.customer_menu.set()
            await bot.send_message(message.from_user.id,
                                   "<b>Отклик с видео отправлен.</b>\n"
                                   "<b>Ожидайте пока Исполнитель примет ваш заказ!</b>")
            not_at_work = await customers_get.customer_all_orders_not_at_work(message.from_user.id)
            at_work = await customers_get.customer_all_orders_in_work(message.from_user.id)
            loading = await customers_get.customer_all_orders_loading(message.from_user.id)
            await bot.send_message(message.from_user.id,
                                   f"{markup_customer.text_menu(len(not_at_work), len(at_work), len(loading))}",
                                   reply_markup=markup_customer.main_menu())


class CustomerCreateTaskLoading:

    @staticmethod
    async def geo_position_from(message: types.Message, state: FSMContext):
        if message.location:
            try:
                n = Nominatim(user_agent=f'FlowWork_{message.from_user.id}')
                loc = f"{message.location.latitude}, {message.location.longitude}"
                address = n.reverse(loc)
                city = address.raw.get("address").get("city")
                if city is None:
                    city = address.raw.get("address").get("town")
                await bot.send_message(message.from_user.id,
                                       f'Город: {city}\n'
                                       f'Адрес: {address.raw.get("address").get("road")}, '
                                       f'{address.raw.get("address").get("house_number")}\n')
                await bot.send_message(message.from_user.id,
                                       "Проверьте пожалуйста координаты, если вы ошиблись "
                                       "вы можете еще раз отправить геопозицию. "
                                       "Если же все в порядке нажмите Все верно",
                                       reply_markup=markup_customer.inline_approve_geo_from_loading())
                async with state.proxy() as data:
                    data["geo_data_from_loading"] = f'{city}, ' \
                                                    f'{address.raw.get("address").get("road")}, ' \
                                                    f'{address.raw.get("address").get("house_number")}'
            except AttributeError:
                pass
        if message.text:
            if message.text == f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад":
                await customer_states.CustomerCreateTask.category_delivery.set()
                await bot.send_message(message.from_user.id,
                                       "Вы вернулись на шаг назад\n"
                                       "Здесь вы можете выбрать <b>категорию Заказа</b>",
                                       reply_markup=markup_customer.category_delivery())
            if message.text != f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад":
                msg = message.text.split()
                if len(msg) == 4:
                    await bot.send_message(message.from_user.id,
                                           f'Город подачи: {msg[0]}\n'
                                           f'Адрес подачи: {msg[1]} {msg[2]} - '
                                           f'{msg[-1]}')
                    await bot.send_message(message.from_user.id,
                                           "Проверьте пожалуйста введенные данные, если вы ошиблись "
                                           "вы можете еще раз отправить адрес.\n"
                                           "Если же все в порядке нажмите Все верно",
                                           reply_markup=markup_customer.inline_approve_geo_from_loading())
                    async with state.proxy() as data:
                        data["geo_data_from_loading"] = message.text
                elif len(msg) == 3:
                    await bot.send_message(message.from_user.id,
                                           f'Город подачи: {msg[0]}\n'
                                           f'Адрес подачи: {msg[1]} - '
                                           f'{msg[-1]}')
                    await bot.send_message(message.from_user.id,
                                           "Проверьте пожалуйста введенные данные, если вы ошиблись "
                                           "вы можете еще раз отправить адрес.\n"
                                           "Если же все в порядке нажмите Все верно",
                                           reply_markup=markup_customer.inline_approve_geo_from_loading())
                    async with state.proxy() as data:
                        data["geo_data_from_loading"] = message.text
                else:
                    await bot.send_message(message.from_user.id,
                                           "Надо ввести данные в формате\n"
                                           "<b>Город Улица Дом</b>")

    @staticmethod
    async def approve_geo_from(callback: types.CallbackQuery):
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        await bot.send_message(callback.from_user.id,
                               "Укажите количество требуемых грузчиков",
                               reply_markup=markup_customer.back())
        await customer_states.CustomerCreateTaskLoading.people.set()

    @staticmethod
    async def count_man_loading(message: types.Message, state: FSMContext):
        if message.text == f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад":
            await customer_states.CustomerCreateTaskLoading.geo_position.set()
            await bot.send_message(message.from_user.id,
                                   "Вы вернулись на шаг назад\n"
                                   "Здесь вы можете указать адрес <b>Куда выезжать грузчикам</b>",
                                   reply_markup=markup_customer.send_my_geo())
        if message.text.isdigit() and int(message.text) <= 10:
            async with state.proxy() as data:
                data["people"] = int(message.text)
            await bot.send_message(message.from_user.id,
                                   "<b>Что нужно делать ?</b>\n"
                                   "<b>Введите описание работ</b>\n"
                                   "<b>Укажите что за груз, его габариты. "
                                   "В общем все детали нужно указывать здесь!</b>",
                                   reply_markup=markup_customer.back())
            await customer_states.CustomerCreateTaskLoading.next()
        elif message.text != f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад":
            await bot.send_message(message.from_user.id,
                                   "Не больше 10\n"
                                   "Надо ввести целое число")

    @staticmethod
    async def description(message: types.Message, state: FSMContext):
        if message.text == f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад":
            await customer_states.CustomerCreateTaskLoading.people.set()
            await bot.send_message(message.from_user.id,
                                   "Вы вернулись на шаг назад\n"
                                   "Здесь вы сможете ввести <b>количество Грузчиков</b>",
                                   reply_markup=markup_customer.back())
        else:
            if len(message.text) > 255:
                await bot.send_message(message.from_user.id,
                                       "Вы ввели слишком длинное описание!"
                                       "Ограничение в описании заказа 255 символов!",
                                       reply_markup=markup_customer.back())
            else:
                async with state.proxy() as data:
                    data["description"] = message.text
                await customer_states.CustomerCreateTaskLoading.next()
                await bot.send_message(message.from_user.id,
                                       "Цена вводится за <b>1 час</b> работы\n"
                                       "Предложите цену исполнителю",
                                       reply_markup=markup_customer.back())

    @staticmethod
    async def price(message: types.Message, state: FSMContext):
        if message.text == f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад":
            await customer_states.CustomerCreateTaskLoading.description.set()
            await bot.send_message(message.from_user.id,
                                   "Вы вернулись на шаг назад\n"
                                   "Здесь вы сможете ввести <b>что надо сделать</b>",
                                   reply_markup=markup_customer.back())
        if message.text.isdigit():
            async with state.proxy() as data:
                data["price"] = message.text
            await bot.send_message(message.from_user.id,
                                   "<b>Введите начало работы</b>\n"
                                   "Пример:\n"
                                   "<b>'Завтра в 11:00'</b> или "
                                   "<b>'Сегодня вечером в 19:00'</b>",
                                   reply_markup=markup_customer.back())
            await customer_states.CustomerCreateTaskLoading.next()
        elif message.text != f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад":
            await bot.send_message(message.from_user.id,
                                   "Надо ввести целое число")

    @staticmethod
    async def start_time(message: types.Message, state: FSMContext):
        if message.text != f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад":
            async with state.proxy() as data:
                data["start_time"] = message.text
            await bot.send_message(message.from_user.id,
                                   "<b>Сколько часов максимум актуален ваш заказ ?</b>",
                                   reply_markup=markup_customer.back())
            await customer_states.CustomerCreateTaskLoading.next()
        if message.text == f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад":
            await customer_states.CustomerCreateTaskLoading.price.set()
            await bot.send_message(message.from_user.id,
                                   "Вы вернулись на шаг назад\n"
                                   "Здесь вы сможете ввести <b>Цену за 1 час</b>",
                                   reply_markup=markup_customer.back())

    @staticmethod
    async def expired_order(message: types.Message, state: FSMContext):
        if message.text == f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад":
            await customer_states.CustomerCreateTaskLoading.start_time.set()
            await bot.send_message(message.from_user.id,
                                   "Вы вернулись на шаг назад\n"
                                   "Здесь вы сможете ввести <b>Начало работ</b>",
                                   reply_markup=markup_customer.back())
        if message.text.isdigit():
            if 1 <= int(message.text) <= 12:
                date = datetime.now() + timedelta(hours=int(message.text))
                await bot.send_message(message.from_user.id,
                                       f"Ваш заказ действует <b>{message.text} часа</b>\n"
                                       f"До {date.strftime('%d %B %Y, %H:%M')}\n"
                                       f"Если по истечении этого времени никто ваш заказ не возьмет\n"
                                       f"Заказ исчезнет автоматически")
                async with state.proxy() as data:
                    data['order_expired'] = date
                await bot.send_message(message.from_user.id,
                                       "Загрузите фото или видео",
                                       reply_markup=markup_customer.photo_or_video_create_task())
                await customer_states.CustomerCreateTaskLoading.next()
            else:
                await bot.send_message(message.from_user.id,
                                       f"Введите от 1 до 12 часов")
        if message.text != f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад" \
                and not message.text.isdigit():
            await bot.send_message(message.from_user.id,
                                   "Нужно ввести цифру\n"
                                   "Введите сколько часов действует ваш заказ")

    @staticmethod
    async def photo_video(message: types.Message, state: FSMContext):
        order_id = f"{datetime.now().strftime('%m_%d')}_{randint(1, 99999)}"
        geolocator = Nominatim(user_agent=f'FlowWork_{message.from_user.id}')
        async with state.proxy() as data:
            data["order_id"] = order_id
        if message.text == "Без фото или видео":
            async with state.proxy() as data:
                await bot.send_message(message.from_user.id,
                                       "Подождите немножко, размещаем ваш заказ")
                await customers_set.customer_add_order_loading(message.from_user.id,
                                                               data.get("geo_data_from_loading"),
                                                               data.get("description"),
                                                               int(data.get("price")),
                                                               data.get("start_time"),
                                                               None,
                                                               None,
                                                               order_id,
                                                               datetime.now().strftime('%d-%m-%Y, %H:%M:%S'),
                                                               data.get("order_expired").strftime('%d-%m-%Y, %H:%M:%S'),
                                                               data.get("people"))
                performers = await general_get.all_performers_auto_send("loading")
                if performers:
                    for i in performers:
                        try:
                            loc_a = geolocator.geocode(data.get("geo_data_from_loading"))
                            loc_a = loc_a.latitude, loc_a.longitude
                            location_result = f"{round(distance.distance(loc_a, i.geo_position).km, 2)} км"
                        except AttributeError:
                            location_result = f"Не получилось определить {config.KEYBOARD.get('FROWNING_FACE')}"
                        await bot.send_message(i.user_id,
                                               f"Новый заказ! От заказчика {message.from_user.id}\n"
                                               f"{config.KEYBOARD.get('DASH') * 14}\n"
                                               f"{config.KEYBOARD.get('A_BUTTON')} "
                                               f"Место работы - <a href='https://yandex.ru/maps/?text="
                                               f"{'+'.join(data.get('geo_data_from').split())}'>"
                                               f"{data.get('geo_data_from')}</a>\n"
                                               f"{config.KEYBOARD.get('BUST_IN_SILHOUETTE')} "
                                               f"Нужно грузчиков - {data.get('people')}\n"
                                               f"{config.KEYBOARD.get('DOLLAR')} "
                                               f"Цена за 1 час - <b>{data.get('price')}</b>\n"
                                               f"{config.KEYBOARD.get('STOPWATCH')} "
                                               f"Начало работы - {data.get('start_time')}\n"
                                               f"{config.KEYBOARD.get('CLIPBOARD')} "
                                               f"Описание - <b>{data.get('description')}</b>\n"
                                               f"{config.KEYBOARD.get('WORLD_MAP')} "
                                               f"<b>Место работы</b> находится в радиусе: "
                                               f"<b>{location_result}</b>\n"
                                               f"{config.KEYBOARD.get('DASH') * 14}",
                                               disable_web_page_preview=True,
                                               reply_markup=markup_performer.
                                               inline_approve_loading(data.get('order_id')))
            await customer_states.CustomerStart.customer_menu.set()
            await bot.send_message(message.from_user.id,
                                   "<b>Отклик без фото или видео отправлен.</b>\n"
                                   "<b>Ожидайте пока Исполнитель примет ваш заказ!</b>")
            not_at_work = await customers_get.customer_all_orders_not_at_work(message.from_user.id)
            at_work = await customers_get.customer_all_orders_in_work(message.from_user.id)
            loading = await customers_get.customer_all_orders_loading(message.from_user.id)
            await bot.send_message(message.from_user.id,
                                   f"{markup_customer.text_menu(len(not_at_work), len(at_work), len(loading))}",
                                   reply_markup=markup_customer.main_menu())
        if message.text == "Загрузить Фото":
            await customer_states.CustomerCreateTaskLoading.photo.set()
            await bot.send_message(message.from_user.id,
                                   f"{message.from_user.first_name} Загрузите фото",
                                   reply_markup=markup_customer.back())
        if message.text == "Загрузить Видео":
            await customer_states.CustomerCreateTaskLoading.video.set()
            await bot.send_message(message.from_user.id,
                                   f"{message.from_user.first_name} Загрузите видео",
                                   reply_markup=markup_customer.back())
        if message.text == f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад":
            await customer_states.CustomerCreateTaskLoading.expired_data.set()
            await bot.send_message(message.from_user.id,
                                   "Вы вернулись на шаг назад\n"
                                   "Здесь вы сможете определить <b>срок истечения вашего Заказа</b>",
                                   reply_markup=markup_customer.back())

    @staticmethod
    async def photo(message: types.Message, state: FSMContext):
        if message.text == f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад":
            await customer_states.CustomerCreateTaskLoading.photo_or_video.set()
            await bot.send_message(message.from_user.id,
                                   "Вы вернулись на шаг назад\n"
                                   "Здесь вы сможете выбрать загрузку с Фото или Видео\n"
                                   "Или можно Без Фото и Видео",
                                   reply_markup=markup_customer.photo_or_video_create_task())
        else:
            try:
                async with state.proxy() as data:
                    data["photo"] = message.photo[2].file_id
                await bot.send_message(message.from_user.id,
                                       "Подождите немножко, размещаем ваш заказ")
                geolocator = Nominatim(user_agent=f'FlowWork_{message.from_user.id}')
                await customers_set.customer_add_order_loading(message.from_user.id,
                                                               data.get("geo_data_from_loading"),
                                                               data.get("description"),
                                                               int(data.get("price")),
                                                               data.get("start_time"),
                                                               data.get("photo"),
                                                               None,
                                                               data.get("order_id"),
                                                               datetime.now().strftime('%d-%m-%Y, %H:%M:%S'),
                                                               data.get("order_expired").strftime('%d-%m-%Y, %H:%M:%S'),
                                                               data.get("people"))
                await general_set.add_review(data.get("order_id"))
                performers = await general_get.all_performers_auto_send("loading")
                if performers:
                    for i in performers:
                        try:
                            loc_a = geolocator.geocode(data.get("geo_data_from_loading"))
                            loc_a = loc_a.latitude, loc_a.longitude
                            location_result = f"{round(distance.distance(loc_a, i.geo_position).km, 2)} км"
                        except AttributeError:
                            location_result = f"Не получилось определить {config.KEYBOARD.get('FROWNING_FACE')}"
                        await bot.send_message(i.user_id,
                                               f"Новый заказ! От заказчика {message.from_user.id}\n"
                                               f"{config.KEYBOARD.get('DASH') * 14}\n"
                                               f"{config.KEYBOARD.get('A_BUTTON')} "
                                               f"Место работы - <a href='https://yandex.ru/maps/?text="
                                               f"{'+'.join(data.get('geo_data_from').split())}'>"
                                               f"{data.get('geo_data_from')}</a>\n"
                                               f"{config.KEYBOARD.get('BUST_IN_SILHOUETTE')} "
                                               f"Нужно грузчиков - {data.get('people')}\n"
                                               f"{config.KEYBOARD.get('DOLLAR')} "
                                               f"Цена за 1 час - <b>{data.get('price')}</b>\n"
                                               f"{config.KEYBOARD.get('STOPWATCH')} "
                                               f"Начало работы - {data.get('start_time')}\n"
                                               f"{config.KEYBOARD.get('CLIPBOARD')} "
                                               f"Описание - <b>{data.get('description')}</b>\n"
                                               f"{config.KEYBOARD.get('WORLD_MAP')} "
                                               f"<b>Место работы</b> находится в радиусе: "
                                               f"<b>{location_result}</b>\n"
                                               f"{config.KEYBOARD.get('DASH') * 14}",
                                               disable_web_page_preview=True,
                                               reply_markup=markup_performer.
                                               inline_approve_loading(data.get('order_id')))
                await customer_states.CustomerStart.customer_menu.set()
                await bot.send_message(message.from_user.id,
                                       "<b>Отклик с фото отправлен.</b>\n"
                                       "<b>Ожидайте пока Исполнитель примет ваш заказ!</b>")
                not_at_work = await customers_get.customer_all_orders_not_at_work(message.from_user.id)
                at_work = await customers_get.customer_all_orders_in_work(message.from_user.id)
                loading = await customers_get.customer_all_orders_loading(message.from_user.id)
                await bot.send_message(message.from_user.id,
                                       f"{markup_customer.text_menu(len(not_at_work), len(at_work), len(loading))}",
                                       reply_markup=markup_customer.main_menu())
            except IndexError:
                pass

    @staticmethod
    async def video(message: types.Message, state: FSMContext):
        if message.text == f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад":
            await customer_states.CustomerCreateTaskLoading.photo_or_video.set()
            await bot.send_message(message.from_user.id,
                                   "Вы вернулись на шаг назад\n"
                                   "Здесь вы сможете выбрать загрузку с Фото или Видео\n"
                                   "Или можно Без Фото и Видео",
                                   reply_markup=markup_customer.photo_or_video_create_task())
        else:
            async with state.proxy() as data:
                data["video"] = message.video.file_id
            await bot.send_message(message.from_user.id,
                                   "Подождите немножко, размещаем ваш заказ")
            geolocator = Nominatim(user_agent=f'FlowWork_{message.from_user.id}')
            await customers_set.customer_add_order_loading(message.from_user.id,
                                                           data.get("geo_data_from_loading"),
                                                           data.get("description"),
                                                           int(data.get("price")),
                                                           data.get("start_time"),
                                                           None,
                                                           data.get("video"),
                                                           data.get("order_id"),
                                                           datetime.now().strftime('%d-%m-%Y, %H:%M:%S'),
                                                           data.get("order_expired").strftime('%d-%m-%Y, %H:%M:%S'),
                                                           data.get("people"))
            await general_set.add_review(data.get("order_id"))
            performers = await general_get.all_performers_auto_send("loading")
            if performers:
                for i in performers:
                    try:
                        loc_a = geolocator.geocode(data.get("geo_data_from_loading"))
                        loc_a = loc_a.latitude, loc_a.longitude
                        location_result = f"{round(distance.distance(loc_a, i.geo_position).km, 2)} км"
                    except AttributeError:
                        location_result = f"Не получилось определить {config.KEYBOARD.get('FROWNING_FACE')}"
                    await bot.send_message(i.user_id,
                                           f"Новый заказ! От заказчика {message.from_user.id}\n"
                                           f"{config.KEYBOARD.get('DASH') * 14}\n"
                                           f"{config.KEYBOARD.get('A_BUTTON')} "
                                           f"Место работы - <a href='https://yandex.ru/maps/?text="
                                           f"{'+'.join(data.get('geo_data_from').split())}'>"
                                           f"{data.get('geo_data_from')}</a>\n"
                                           f"{config.KEYBOARD.get('BUST_IN_SILHOUETTE')} "
                                           f"Нужно грузчиков - {data.get('people')}\n"
                                           f"{config.KEYBOARD.get('DOLLAR')} "
                                           f"Цена за 1 час - <b>{data.get('price')}</b>\n"
                                           f"{config.KEYBOARD.get('STOPWATCH')} "
                                           f"Начало работы - {data.get('start_time')}\n"
                                           f"{config.KEYBOARD.get('CLIPBOARD')} "
                                           f"Описание - <b>{data.get('description')}</b>\n"
                                           f"{config.KEYBOARD.get('WORLD_MAP')} "
                                           f"<b>Место работы</b> находится в радиусе: "
                                           f"<b>{location_result}</b>\n"
                                           f"{config.KEYBOARD.get('DASH') * 14}",
                                           disable_web_page_preview=True,
                                           reply_markup=markup_performer.
                                           inline_approve_loading(data.get('order_id')))
            await customer_states.CustomerStart.customer_menu.set()
            await bot.send_message(message.from_user.id,
                                   "<b>Отклик с видео отправлен.</b>\n"
                                   "<b>Ожидайте пока Исполнитель примет ваш заказ!</b>")
            not_at_work = await customers_get.customer_all_orders_not_at_work(message.from_user.id)
            at_work = await customers_get.customer_all_orders_in_work(message.from_user.id)
            loading = await customers_get.customer_all_orders_loading(message.from_user.id)
            await bot.send_message(message.from_user.id,
                                   f"{markup_customer.text_menu(len(not_at_work), len(at_work), len(loading))}",
                                   reply_markup=markup_customer.main_menu())
