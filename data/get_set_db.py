import logging
from data.create_db import Database


class GlobalGetDB(Database):
    logger = logging.getLogger("bot.data.global_get_db")

    def all_customers(self):
        self.logger.info('Функция выгрузки всех заказчиков')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM customers"
            )
            return cursor.fetchall()

    def all_performers(self):
        self.logger.info('Функция выгрузки всех исполнителей')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM performers"
            )
            return cursor.fetchall()

    def all_orders(self):
        self.logger.info(f'Функция просмотра всех заказов')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM orders;"
            )
            return cursor.fetchall()

    def all_orders_status(self):
        self.logger.info(f'Функция просмотра статуса всех заказов')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM orders_status;"
            )
            return cursor.fetchone()

    def all_orders_reviews(self):
        self.logger.info(f'Функция просмотра всех отзывов')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM reviews;"
            )
            return cursor.fetchall()

    def check_details_status(self, user_id, order_id):
        self.logger.info(f'Пользователь {user_id} проверяет статус заказа {order_id}')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT performer_status, customer_status FROM orders_status "
                "WHERE order_id = %(order_id)s;", {
                    'order_id': order_id,
                }
            )
            return cursor.fetchone()

    def check_commission_category(self, order_id, category_delivery):
        self.logger.info(f'Проверяется комиссия заказа {order_id}')
        with self.connection.cursor() as cursor:
            cursor.execute(
                f"SELECT {category_delivery} FROM commission;"
            )
            return cursor.fetchone()

    def check_commission_for_customer_and_performer(self):
        self.logger.info(f'Проверяется комиссия Заказчика и Исполнителя')
        with self.connection.cursor() as cursor:
            cursor.execute(
                f"SELECT customer, performer FROM commission;"
            )
            return cursor.fetchone()

    def check_commission_promo(self, user_id):
        self.logger.info(f'Проверяется промо комиссия')
        with self.connection.cursor() as cursor:
            cursor.execute(
                f"SELECT percent, promo_time FROM commission_promo "
                "WHERE user_id = %(user_id)s;", {
                    'user_id': user_id,
                }
            )
            return cursor.fetchone()

    def get_payment(self, bill_id):
        self.logger.info('Функция проверки платежа в БД')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM payment WHERE bill_id = %(bill_id)s;", {
                    'bill_id': bill_id,
                }
            )
            result = cursor.fetchmany(1)
            if not bool(len(result)):
                return False
            return result[0]

    def get_payment_exists(self, user_id):
        self.logger.info('Функция проверки возможных остатков в БД')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM payment WHERE user_id = %(user_id)s;", {
                    'user_id': user_id,
                }
            )
            return cursor.fetchone()

    def check_orders_expired(self):
        self.logger.info(f'Проверяется срок истекания заказов каждые 60 секунд')
        with self.connection.cursor() as cursor:
            cursor.execute(
                f"SELECT order_id, order_expired FROM orders "
                "WHERE order_get IS NULL;"
            )
            return cursor.fetchall()

    def check_orders_status(self):
        with self.connection.cursor() as cursor:
            cursor.execute(
                f"SELECT performer_status, customer_status, order_id FROM orders_status;"
            )
            return cursor.fetchall()

    def check_private_chat_status(self, user_id):
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT user_id FROM private_chat "
                "WHERE user_id = %(user_id)s;", {
                    'user_id': user_id,
                }
            )
            return cursor.fetchone()

    def check_private_chat_count_word(self, user_id):
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT count_word FROM private_chat "
                "WHERE user_id = %(user_id)s;", {
                    'user_id': user_id,
                }
            )
            return cursor.fetchone()


class GlobalSetDB(Database):
    logger = logging.getLogger("bot.data.global_set_db")

    def block_user(self, block, type_user, user_id):
        if block:
            self.logger.info(f'Администратор блокирует пользователя {user_id}')
            with self.connection.cursor() as cursor:
                cursor.execute(
                    f"UPDATE {type_user} SET ban = 1 WHERE user_id = %(user_id)s;", {
                        'user_id': user_id,
                    }
                )
                self.connection.commit()
        else:
            self.logger.info(f'Администратор разблокирует пользователя {user_id}')
            with self.connection.cursor() as cursor:
                cursor.execute(
                    f"UPDATE {type_user} SET ban = 0 WHERE user_id = %(user_id)s;", {
                        'user_id': user_id,
                    }
                )
                self.connection.commit()

    def close_order(self, order_id):
        self.logger.info(f'Удаляется заказ {order_id} из состоянии статуса')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM orders_status WHERE order_id = %(order_id)s;", {
                    'order_id': order_id,
                }
            )
            self.connection.commit()

    def close_order_completed(self, order_id, order_end):
        self.logger.info(f'Ставится пометка completed в orders {order_id}. Время ззавершения '
                         f'{order_end}')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "UPDATE orders SET completed = 1, order_end = %(order_end)s WHERE order_id = %(order_id)s;", {
                    'order_id': order_id,
                    'order_end': order_end,
                }
            )
            self.connection.commit()

    def get_order_timestamp(self, order_id, order_get):
        self.logger.info(f'Исполнитель берёт заказ {order_id} - {order_get}')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "UPDATE orders SET order_get = %(order_get)s WHERE order_id = %(order_id)s;", {
                    'order_id': order_id,
                    'order_get': order_get,
                }
            )
            self.connection.commit()

    def add_review(self, order_id):
        self.logger.info(f'Добавляется возможность оставлять отзывы в заказе - {order_id}')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO reviews (review_from_customer, review_from_performer, order_id) "
                "VALUES (NULL, NULL, %(order_id)s);", {
                    'order_id': order_id,
                }
            )
            self.connection.commit()

    def set_commission_for_performer(self, user_id, commission):
        self.logger.info(f'Взымается комиссия с Исполнителя {user_id}')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "UPDATE performers SET performer_money = performer_money - %(commission)s "
                "WHERE user_id = %(user_id)s;", {
                    'commission': commission,
                    'user_id': user_id,
                }
            )
            self.connection.commit()

    def set_commission_for_customer(self, user_id, commission):
        self.logger.info(f'Взымается комиссия с Заказчика {user_id}')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "UPDATE customers SET customer_money = customer_money - %(commission)s "
                "WHERE user_id = %(user_id)s;", {
                    'commission': commission,
                    'user_id': user_id,
                }
            )
            self.connection.commit()

    def add_new_price(self, order_id, new_price):
        self.logger.info(f'Добавляется новая цена в заказ - {order_id}')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "UPDATE orders SET price = %(new_price)s WHERE order_id = %(order_id)s;", {
                    'order_id': order_id,
                    'new_price': new_price,
                }
            )
            self.connection.commit()

    def set_commission_for_promo(self, user_id, percent, promo_time):
        self.logger.info(f'Добавляется временное промо для {user_id} '
                         f'коммиссия - {percent}, время - {promo_time}')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO commission_promo (user_id, percent, promo_time) "
                "VALUES (%(user_id)s, %(percent)s, %(promo_time)s);", {
                    'user_id': user_id,
                    'percent': percent,
                    'promo_time': promo_time,
                }
            )
            self.connection.commit()

    def add_payment(self, user_id, money, bill_id):
        self.logger.info('Функция добавления платежа в БД')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO payment (user_id, money, bill_id) "
                "VALUES (%(user_id)s, %(money)s, %(bill_id)s);", {
                    'user_id': user_id,
                    'money': money,
                    'bill_id': bill_id,
                }
            )
            self.connection.commit()

    def delete_payment(self,  bill_id):
        self.logger.info('Функция удаления платежа из БД')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM payment WHERE bill_id = %(bill_id)s;", {
                    'bill_id': bill_id,
                }
            )
            self.connection.commit()

    def delete_payment_exists(self,  user_id):
        self.logger.info('Функция удаления остатка платежа из БД')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM payment WHERE user_id = %(user_id)s;", {
                    'user_id': user_id,
                }
            )
            self.connection.commit()

    def private_chat_money(self, user_id):
        self.logger.info(f'Взимается плата 300 рублей за приватный чат с {user_id}')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "UPDATE performers SET performer_money = performer_money - 300 WHERE user_id = %(user_id)s;", {
                    'user_id': user_id,
                }
            )
            self.connection.commit()

    def private_chat_add(self, user_id, count_word, enter_date):
        self.logger.info(f'Добавляется новый Исполнитель {user_id} в закрытый чат')
        with self.connection.cursor() as cursor:
            cursor.execute(
                f"INSERT INTO private_chat (user_id, enter_date, count_word) "
                f"VALUES (%(user_id)s, %(enter_date)s, %(count_word)s);", {
                    'user_id': user_id,
                    'enter_date': enter_date,
                    'count_word': count_word,
                }
            )
            self.connection.commit()

    def order_expired_delete(self, order_id):
        self.logger.info('Функция удаления платежа из БД')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM orders WHERE order_id = %(order_id)s;", {
                    'order_id': order_id,
                }
            )
            self.connection.commit()

    def order_status_delete(self, order_id):
        self.logger.info('Функция удаления заказа из статуса при завершении с обоих сторон')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM orders_status WHERE order_id = %(order_id)s;", {
                    'order_id': order_id,
                }
            )
            self.connection.commit()

    def private_chat_change_count_word(self, user_id):
        with self.connection.cursor() as cursor:
            cursor.execute(
                "UPDATE private_chat SET count_word = count_word + 1 "
                "WHERE user_id = %(user_id)s;", {
                    'user_id': user_id,
                }
            )
            self.connection.commit()

    def private_chat_delete_user(self, user_id):
        with self.connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM private_chat WHERE user_id = %(user_id)s;", {
                    'user_id': user_id,
                }
            )
            self.connection.commit()

    def order_rating_change_plus(self, order_id):
        with self.connection.cursor() as cursor:
            cursor.execute(
                "UPDATE orders SET order_rating = order_rating + 1 "
                "WHERE order_id = %(order_id)s;", {
                    'order_id': order_id,
                }
            )
            self.connection.commit()

    def order_rating_change_minus(self, order_id):
        with self.connection.cursor() as cursor:
            cursor.execute(
                "UPDATE orders SET order_rating = order_rating - 1 "
                "WHERE order_id = %(order_id)s;", {
                    'order_id': order_id,
                }
            )
            self.connection.commit()


class CustomerGetDB(Database):
    logger = logging.getLogger("bot.data.customer_get_db")

    def customer_exists(self, user_id: int):
        self.logger.info('Заказчик проверяет себя на наличие в БД')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM customers WHERE user_id = %(user_id)s;", {
                    'user_id': user_id,
                }
            )
            return cursor.fetchone()

    def customer_ban(self, user_id):
        self.logger.info('Заказчик проверяет себя на БАН')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT ban FROM customers WHERE user_id = %(user_id)s", {
                    'user_id': user_id,
                }
            )
            return cursor.fetchone()

    def customer_money(self, user_id):
        self.logger.info('Заказчик проверяет свой баланс')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT customer_money FROM customers WHERE user_id = %(user_id)s", {
                    'user_id': user_id,
                }
            )
            return cursor.fetchone()

    def customer_rating(self, user_id):
        self.logger.info('Заказчик проверяет свой рейтинг')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT customer_rating FROM customers WHERE user_id = %(user_id)s", {
                    'user_id': user_id,
                }
            )
            return cursor.fetchone()

    def customer_checks_performer_rating(self, user_id):
        self.logger.info('Заказчик проверяет рейтинг Исполнителя')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT performer_rating FROM performers WHERE user_id = %(user_id)s", {
                    'user_id': user_id,
                }
            )
            return cursor.fetchone()[0]

    def customer_count_orders(self, user_id):
        self.logger.info('Заказчик проверяет количество своих заказов')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM orders WHERE user_id = %(user_id)s;", {
                    'user_id': user_id,
                }
            )
            return cursor.fetchone()[0]

    def customer_in_work_orders(self, user_id):
        self.logger.info('Заказчик проверяет количество своих заказов в работе')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM orders WHERE user_id = %(user_id)s AND in_work > 1 AND completed = 0 "
                "AND order_cancel IS NULL;", {
                    'user_id': user_id,
                }
            )
            return cursor.fetchone()[0]

    def customer_complete_orders(self, user_id):
        self.logger.info('Заказчик проверяет количество своих выполненных заказов')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM orders WHERE user_id = %(user_id)s AND completed = 1;", {
                    'user_id': user_id,
                }
            )
            return cursor.fetchone()[0]

    def customer_canceled_orders_by_customer(self, user_id):
        self.logger.info('Заказчик проверяет количество своих отменённых заказов')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM orders WHERE user_id = %(user_id)s AND order_cancel IS NOT NULL;", {
                    'user_id': user_id,
                }
            )
            return cursor.fetchone()[0]

    def customer_all_orders(self, user_id):
        self.logger.info('Заказчик выгружает список всех своих заказов')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM orders "
                "WHERE user_id = %(user_id)s AND completed = 0 AND order_cancel IS NULL;", {
                    'user_id': user_id,
                }
            )
            return cursor.fetchall()

    def customer_all_completed_orders(self, user_id):
        self.logger.info('Заказчик выгружает список всех своих завершенных заказов')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM orders "
                "WHERE user_id = %(user_id)s AND completed = 1;", {
                    'user_id': user_id,
                }
            )
            return cursor.fetchall()

    def customer_in_work_order(self, order_id):
        self.logger.info(f'Заказчик проверяет взят ли заказ')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT in_work FROM orders WHERE order_id = %(order_id)s;", {
                    'order_id': order_id,
                }
            )
            return cursor.fetchone()

    def customer_view_order(self, order_id):
        self.logger.info(f'Заказчик просматривает заказ {order_id}')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM orders WHERE order_id = %(order_id)s;", {
                    'order_id': order_id,
                }
            )
            return cursor.fetchone()

    def customer_get_complete_order(self, order_id):
        self.logger.info('Заказчик выгружает конкретный завершенный заказ')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM orders "
                "WHERE order_id = %(order_id)s AND completed = 1;", {
                    'order_id': order_id,
                }
            )
            return cursor.fetchone()

    def customer_get_status_order(self, order_id):
        self.logger.info('Заказчик просматривает статус заказа')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT customer_status FROM orders_status "
                "WHERE order_id = %(order_id)s;", {
                    'order_id': order_id,
                }
            )
            return cursor.fetchone()

    def customer_get_finished_orders_year(self, user_id, year):
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM orders WHERE EXTRACT(YEAR FROM orders.order_end) = %(year)s "
                "AND user_id = %(user_id)s;", {
                    'user_id': user_id,
                    'year': year,
                }
            )
            return cursor.fetchall()

    def customer_get_finished_orders_month(self, user_id, year, month):
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM orders WHERE EXTRACT(YEAR FROM orders.order_end) = %(year)s "
                "AND EXTRACT(MONTH FROM orders.order_end) = %(month)s "
                "AND user_id = %(user_id)s;", {
                    'user_id': user_id,
                    'year': year,
                    'month': month,
                }
            )
            return cursor.fetchall()

    def customer_get_finished_orders_day(self, user_id, year, month, day):
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM orders WHERE EXTRACT(YEAR FROM orders.order_end) = %(year)s "
                "AND EXTRACT(MONTH FROM orders.order_end) = %(month)s "
                "AND EXTRACT(DAY FROM orders.order_end) = %(day)s "
                "AND user_id = %(user_id)s;", {
                    'user_id': user_id,
                    'year': year,
                    'month': month,
                    'day': day,
                }
            )
            return cursor.fetchall()


class CustomerSetDB(Database):
    logger = logging.getLogger("bot.data.customer_set_db")

    def customer_add(self, user_id: int, username, telephone, first_name, last_name):
        self.logger.info('Заказчик добавляет себя в БД')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO customers (user_id, username, telephone, first_name, last_name) "
                "VALUES (%(user_id)s, %(username)s, %(telephone)s, %(first_name)s, %(last_name)s);", {
                    'user_id': user_id,
                    'username': username,
                    'telephone': telephone,
                    'first_name': first_name,
                    'last_name': last_name,
                }
            )
            self.connection.commit()

    def customer_add_order(self, user_id, geo_position_from, geo_position_to, title, price, description,
                           image, video, order_id, order_create, category_delivery, performer_category,
                           order_expired, order_worth):
        self.logger.info(f'Заказчик {user_id} добавляет заказ {order_id}')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO orders (user_id, geo_position_from, geo_position_to, title, price, description, "
                "image, video, order_id, order_create, category_delivery, performer_category, order_expired, "
                "order_worth) "
                "VALUES (%(user_id)s, %(geo_position_from)s, %(geo_position_to)s, %(title)s, "
                "%(price)s, %(description)s, %(image)s, %(video)s, %(order_id)s, %(order_create)s, "
                "%(category_delivery)s, %(performer_category)s, %(order_expired)s, %(order_worth)s);"
                "UPDATE customers SET create_orders = create_orders + 1 WHERE user_id = %(user_id)s;", {
                    'user_id': user_id,
                    'geo_position_from': geo_position_from,
                    'geo_position_to': geo_position_to,
                    'title': title,
                    'price': price,
                    'description': description,
                    'image': image,
                    'video': video,
                    'order_id': order_id,
                    'order_create': order_create,
                    'category_delivery': category_delivery,
                    'performer_category': performer_category,
                    'order_expired': order_expired,
                    'order_worth': order_worth,
                }
            )
            self.connection.commit()

    def customer_change_order(self, order_id, change, result):
        self.logger.info(f'Заказчик редактирует {change}, заказ - {order_id}')
        with self.connection.cursor() as cursor:
            cursor.execute(
                f"UPDATE orders SET {change} = %(result)s WHERE order_id = %(order_id)s;", {
                    'order_id': order_id,
                    'result': result,
                }
            )
            self.connection.commit()

    def customer_set_block_order(self, order_id, block: int):
        self.logger.info(f'Заказчик зашел/вышел из редактировании заказа {order_id}')
        with self.connection.cursor() as cursor:
            cursor.execute(
                f"UPDATE orders SET block = {block} WHERE order_id = %(order_id)s;", {
                    'order_id': order_id,
                }
            )
            self.connection.commit()

    def customer_set_order_status(self, order_id):
        self.logger.info(f'Заказчик ставит ВЫПОЛНЕНО в состоянии заказа {order_id}')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "UPDATE orders_status SET customer_status = 1 WHERE order_id = %(order_id)s;", {
                    'order_id': order_id,
                }
            )
            self.connection.commit()

    def customer_cancel_order(self, order_id, order_cancel):
        self.logger.info(f'Заказчик ОТМЕНЯЕТ заказ {order_id}')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM orders_status WHERE order_id = %(order_id)s;"
                "UPDATE orders SET order_cancel = %(order_cancel)s, completed = NULL WHERE order_id = %(order_id)s", {
                    'order_id': order_id,
                    'order_cancel': order_cancel,
                }
            )
            self.connection.commit()

    def customer_set_rating_to_performer(self, user_id, input_customer):
        self.logger.info('Заказчик ставит оценку Исполнителю')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "UPDATE performers SET performer_rating = "
                "(performer_rating + %(input_customer)s) / 2 WHERE user_id = %(user_id)s", {
                    'user_id': user_id,
                    'input_customer': input_customer,
                }
            )
            self.connection.commit()

    def customer_set_rating_to_performer_in_review_db(self, order_id, customer_rating):
        self.logger.info('Ставится оценка Заказчика в таблицу Отзывы')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "UPDATE reviews SET rating_from_customer = %(customer_rating)s "
                "WHERE order_id = %(order_id)s", {
                    'order_id': order_id,
                    'customer_rating': customer_rating,
                }
            )
            self.connection.commit()

    def customer_set_review_to_performer(self, order_id, customer_review: str):
        self.logger.info('Заказчик оставляет отзыв Исполнителю')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "UPDATE reviews SET review_from_customer = %(customer_review)s "
                "WHERE order_id = %(order_id)s", {
                    'order_id': order_id,
                    'customer_review': customer_review,
                }
            )
            self.connection.commit()


class PerformerGetDB(Database):
    logger = logging.getLogger("bot.data.performer_get_db")

    def performer_exists(self, user_id: int):
        self.logger.info('Исполнитель проверяет себя на наличие в БД')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM performers WHERE user_id = %(user_id)s;", {
                    'user_id': user_id,
                }
            )
            return cursor.fetchone()

    def performer_ban(self, user_id):
        self.logger.info('Исполнитель проверяет себя на БАН')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT ban FROM performers WHERE user_id = %(user_id)s", {
                    'user_id': user_id,
                }
            )
            return cursor.fetchone()

    def performer_money(self, user_id):
        self.logger.info('Исполнитель проверяет свой баланс')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT performer_money FROM performers WHERE user_id = %(user_id)s", {
                    'user_id': user_id,
                }
            )
            return cursor.fetchone()[0]

    def performer_rating(self, user_id):
        self.logger.info('Исполнитель проверяет свой рейтинг')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT performer_rating FROM performers WHERE user_id = %(user_id)s", {
                    'user_id': user_id,
                }
            )
            return cursor.fetchone()

    def performer_checks_all_orders(self, user_id, performer_category):
        self.logger.info('Исполнитель проверяет все доступные заказы')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM orders WHERE in_work = 0 AND block = 0 "
                "AND order_get IS NULL AND order_cancel IS NULL AND user_id != %(user_id)s "
                "AND performer_category IN (%(any)s, %(performer_category)s);", {
                    'user_id': user_id,
                    'performer_category': performer_category,
                    'any': 'any',
                }
            )
            return cursor.fetchall()

    def performer_checks_all_orders_with_category(self, user_id, performer_category, category_delivery):
        self.logger.info('Исполнитель проверяет все доступные заказы')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM orders WHERE in_work = 0 AND block = 0 "
                "AND order_get IS NULL AND order_cancel IS NULL AND user_id != %(user_id)s "
                "AND performer_category IN (%(any)s, %(performer_category)s) "
                "AND category_delivery = %(category_delivery)s;", {
                    'user_id': user_id,
                    'performer_category': performer_category,
                    'any': 'any',
                    'category_delivery': category_delivery,
                }
            )
            return cursor.fetchall()

    def performer_view_order(self, order_id):
        self.logger.info(f'Исполнитель просматривает заказ {order_id}')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM orders WHERE order_id = %(order_id)s;", {
                    'order_id': order_id,
                }
            )
            return cursor.fetchone()

    def performer_view_list_orders(self, user_id):
        self.logger.info(f'Исполнитель {user_id} просматривает взятые заказы')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM orders WHERE in_work = %(user_id)s AND completed = 0 "
                "AND order_cancel IS NULL;", {
                    'user_id': user_id,
                }
            )
            return cursor.fetchall()

    def performer_view_count_all_orders(self, user_id):
        self.logger.info(f'Исполнитель {user_id} проверяет количество взятых заказов')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT get_orders FROM performers;", {
                    'user_id': user_id,
                }
            )
            return cursor.fetchone()

    def performer_view_count_in_work_orders(self, user_id):
        self.logger.info(f'Исполнитель {user_id} проверяет количество заказов в работе')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM orders WHERE in_work = %(user_id)s AND completed = 0 "
                "AND order_cancel IS NULL;", {
                    'user_id': user_id,
                }
            )
            return cursor.fetchone()

    def performer_view_count_complete_orders(self, user_id):
        self.logger.info(f'Исполнитель {user_id} проверяет количество выполненных заказов')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM orders WHERE in_work = %(user_id)s AND completed = 1;", {
                    'user_id': user_id,
                }
            )
            return cursor.fetchone()

    def performer_view_count_canceled_orders_by_performer(self, user_id):
        self.logger.info(f'Исполнитель {user_id} проверяет количество отмененных заказов')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT canceled_orders FROM performers;", {
                    'user_id': user_id,
                }
            )
            return cursor.fetchone()

    def performer_checks_customer_user_id(self, user_id, order_id):
        self.logger.info(f'Исполнитель {user_id} проверяет user_id ЗАКАЗЧИКА')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT user_id FROM orders WHERE order_id = %(order_id)s;", {
                    'order_id': order_id,
                }
            )
            return cursor.fetchone()

    def performer_all_completed_orders(self, user_id):
        self.logger.info('Исполнитель выгружает список всех своих завершенных заказов')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM orders "
                "WHERE in_work = %(user_id)s AND completed = 1;", {
                    'user_id': user_id,
                }
            )
            return cursor.fetchall()

    def performer_get_complete_order(self, order_id):
        self.logger.info('Исполнитель выгружает конкретный завершенный заказ')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM orders "
                "WHERE order_id = %(order_id)s AND completed = 1;", {
                    'order_id': order_id,
                }
            )
            return cursor.fetchone()

    def performer_get_status_order(self, order_id):
        self.logger.info('Исполнитель просматривает статус заказа')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT performer_status FROM orders_status "
                "WHERE order_id = %(order_id)s;", {
                    'order_id': order_id,
                }
            )
            return cursor.fetchone()

    def performer_get_finished_orders_year(self, user_id, year):
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM orders WHERE EXTRACT(YEAR FROM orders.order_end) = %(year)s "
                "AND in_work = %(user_id)s;", {
                    'user_id': user_id,
                    'year': year,
                }
            )
            return cursor.fetchall()

    def performer_get_finished_orders_month(self, user_id, year, month):
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM orders WHERE EXTRACT(YEAR FROM orders.order_end) = %(year)s "
                "AND EXTRACT(MONTH FROM orders.order_end) = %(month)s "
                "AND in_work = %(user_id)s;", {
                    'user_id': user_id,
                    'year': year,
                    'month': month,
                }
            )
            return cursor.fetchall()

    def performer_get_finished_orders_day(self, user_id, year, month, day):
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM orders WHERE EXTRACT(YEAR FROM orders.order_end) = %(year)s "
                "AND EXTRACT(MONTH FROM orders.order_end) = %(month)s "
                "AND EXTRACT(DAY FROM orders.order_end) = %(day)s "
                "AND in_work = %(user_id)s;", {
                    'user_id': user_id,
                    'year': year,
                    'month': month,
                    'day': day,
                }
            )
            return cursor.fetchall()

    def performer_trying_change_self_category(self, user_id):
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT performer_category_limit FROM performers "
                "WHERE user_id = %(user_id)s;", {
                    'user_id': user_id,
                }
            )
            return cursor.fetchone()

    def performer_check_order_rating(self, order_id, user_id):
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT rating FROM orders_rating "
                "WHERE user_id = %(user_id)s AND order_id = %(order_id)s;", {
                    'order_id': order_id,
                    'user_id': user_id,
                }
            )
            return cursor.fetchone()


class PerformerSetDB(Database):
    logger = logging.getLogger("bot.data.performer_set_db")

    def performer_add(self, user_id: int, username, telephone, first_name, last_name):
        self.logger.info('Исполнитель добавляет себя в БД')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO performers (user_id, username, telephone, first_name, last_name) "
                "VALUES (%(user_id)s, %(username)s, %(telephone)s, %(first_name)s, %(last_name)s);", {
                    'user_id': user_id,
                    'username': username,
                    'telephone': telephone,
                    'first_name': first_name,
                    'last_name': last_name,
                }
            )
            self.connection.commit()

    def performer_set_order(self, user_id, order_id):
        self.logger.info(f'Исполнитель {user_id} берёт заказ {order_id}')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "UPDATE orders SET in_work = %(user_id)s WHERE order_id = %(order_id)s;"
                "UPDATE performers SET get_orders = get_orders + 1 WHERE user_id = %(user_id)s;", {
                    'user_id': user_id,
                    'order_id': order_id,
                }
            )
            self.connection.commit()

    def performer_new_order_status(self, order_id):
        self.logger.info(f'Исполнитель ВЗЯВ заказ {order_id} добавляет его в состоянии статуса')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO orders_status (order_id) VALUES (%(order_id)s);", {
                    'order_id': order_id,
                }
            )
            self.connection.commit()

    def performer_cancel_order(self, order_id):
        self.logger.info(f'Исполнитель отменяет заказ {order_id}')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "UPDATE orders SET in_work = 0, order_get = NULL WHERE order_id = %(order_id)s;"
                "UPDATE performers SET canceled_orders = canceled_orders + 1;"
                "DELETE FROM orders_status WHERE order_id = %(order_id)s;", {
                    'order_id': order_id,
                }
            )
            self.connection.commit()

    def performer_set_order_status(self, order_id):
        self.logger.info(f'Исполнитель ставит ВЫПОЛНЕНО в состоянии заказа {order_id}')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "UPDATE orders_status SET performer_status = 1 WHERE order_id = %(order_id)s;", {
                    'order_id': order_id,
                }
            )
            self.connection.commit()

    def performer_set_commission_for_complete(self, user_id, performer_money):
        self.logger.info(f'Взымается комиссия с Исполнителя за завершенный заказ')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "UPDATE performers SET performer_money = %(performer_money)s WHERE user_id = %(user_id)s;", {
                    'user_id': user_id,
                    'performer_money': performer_money,
                }
            )
            self.connection.commit()

    def performer_set_commission_for_cancel(self, user_id, commission):
        self.logger.info(f'Взымается комиссия с Исполнителя за отменённый заказ')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "UPDATE performers SET performer_money = performer_money - %(commission)s WHERE user_id = %(user_id)s;",
                {
                    'user_id': user_id,
                    'commission': commission,
                }
            )
            self.connection.commit()

    def performer_set_rating_to_customer(self, user_id, input_performer):
        self.logger.info('Исполнитель ставит оценку Заказчику')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "UPDATE customers SET customer_rating = "
                "(customer_rating + %(input_performer)s) / 2 WHERE user_id = %(user_id)s", {
                    'user_id': user_id,
                    'input_performer': input_performer,
                }
            )
            self.connection.commit()

    def performer_set_review_to_customer(self, order_id, performer_review: str):
        self.logger.info('Исполнитель оставляет отзыв Заказчику')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "UPDATE reviews SET review_from_performer = %(performer_review)s "
                "WHERE order_id = %(order_id)s", {
                    'order_id': order_id,
                    'performer_review': performer_review,
                }
            )
            self.connection.commit()

    def performer_set_rating_to_customer_in_review_db(self, order_id, performer_rating):
        self.logger.info('Ставится оценка Исполнителя в таблицу Отзывы')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "UPDATE reviews SET rating_from_performer = %(performer_rating)s "
                "WHERE order_id = %(order_id)s", {
                    'order_id': order_id,
                    'performer_rating': performer_rating,
                }
            )
            self.connection.commit()

    def performer_set_self_status(self, user_id, performer_category, perf_cat_limit):
        self.logger.info(f'Исполнитель {user_id} меняет свой статус на {performer_category}')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "UPDATE performers SET performer_category = %(performer_category)s "
                "WHERE user_id = %(user_id)s;"
                "UPDATE performers SET performer_category_limit = %(perf_cat_limit)s "
                "WHERE user_id = %(user_id)s;", {
                    'user_id': user_id,
                    'performer_category': performer_category,
                    'perf_cat_limit': perf_cat_limit,
                }
            )
            self.connection.commit()

    def set_money(self, user_id, money):
        self.logger.info('Функция обновления баланса пользователя')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "UPDATE performers SET performer_money = %(money)s WHERE user_id = %(user_id)s;", {
                    'money': money,
                    'user_id': user_id,
                }
            )
            self.connection.commit()

    def performer_set_order_rating(self, order_id, rating, user_id):
        self.logger.info(f'Исполнитель {user_id} ставит {rating} заказу {order_id}')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO orders_rating (order_id, rating, user_id) "
                "VALUES (%(order_id)s, %(rating)s, %(user_id)s);", {
                    'order_id': order_id,
                    'rating': rating,
                    'user_id': user_id,
                }
            )
            self.connection.commit()


class AdminGetDB(Database):
    logger = logging.getLogger("bot.data.admin_get_db")

    def admin_exists(self, user_id: int):
        self.logger.info('Админ проверяет себя на наличие в БД')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM admins WHERE user_id = %(user_id)s;", {
                    'user_id': user_id,
                }
            )
            return cursor.fetchone()

    def admin_check_users(self, type_user: str, user_id: int):
        self.logger.info('Админ ищет пользователя в БД по user_id')
        with self.connection.cursor() as cursor:
            cursor.execute(
                f"SELECT * FROM {type_user} WHERE user_id = %(user_id)s;", {
                    'user_id': user_id,
                }
            )
            return cursor.fetchone()

    def admin_check_users_first_name(self, type_user: str, first_name):
        self.logger.info('Админ ищет пользователя в БД по first_name')
        with self.connection.cursor() as cursor:
            cursor.execute(
                f"SELECT * FROM {type_user} WHERE first_name LIKE '{first_name}%';"
            )
            return cursor.fetchall()

    def admin_check_users_username(self, type_user: str, username):
        self.logger.info('Админ ищет пользователя в БД по username')
        with self.connection.cursor() as cursor:
            cursor.execute(
                f"SELECT * FROM {type_user} WHERE username LIKE '{username}%';"
            )
            return cursor.fetchall()

    def admin_check_order(self, order_id):
        self.logger.info(f'Админ просмотривает заказ {order_id}')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM orders WHERE order_id = %(order_id)s;", {
                    'order_id': order_id,
                }
            )
            return cursor.fetchone()

    def admin_check_review(self, order_id):
        self.logger.info(f'Админ ищёт отзыв по заказу {order_id}')
        with self.connection.cursor() as cursor:
            cursor.execute(
                f"SELECT reviews.id, reviews.review_from_customer, reviews.review_from_performer, "
                f"reviews.rating_from_customer, reviews.rating_from_performer FROM orders "
                f"INNER JOIN reviews ON orders.order_id=reviews.order_id "
                f"WHERE orders.order_id = %(order_id)s;", {
                    'order_id': order_id,
                }
            )
            return cursor.fetchall()

    def admin_check_all_customers(self):
        self.logger.info('Админ выгружает всех Заказчиков')
        with self.connection.cursor() as cursor:
            cursor.execute(
                f"SELECT * FROM customers;"
            )
            return cursor.fetchall()

    def admin_check_all_performers(self):
        self.logger.info('Админ выгружает всех Исполнителей')
        with self.connection.cursor() as cursor:
            cursor.execute(
                f"SELECT * FROM performers;"
            )
            return cursor.fetchall()

    def admin_check_all_orders(self):
        self.logger.info('Админ выгружает все Заказы')
        with self.connection.cursor() as cursor:
            cursor.execute(
                f"SELECT * FROM orders;"
            )
            return cursor.fetchall()

    def admin_check_all_completed_orders(self):
        self.logger.info('Админ выгружает все выполненные Заказы')
        with self.connection.cursor() as cursor:
            cursor.execute(
                f"SELECT * FROM orders WHERE completed = 1;"
            )
            return cursor.fetchall()

    def admin_check_all_orders_categories(self):
        self.logger.info('Админ выгружает все выполненные Заказы')
        with self.connection.cursor() as cursor:
            cursor.execute(
                f"SELECT category_delivery FROM orders;"
            )
            return cursor.fetchall()

    def admin_check_commission(self):
        self.logger.info(f'Админ проверяет коммиссию')
        with self.connection.cursor() as cursor:
            cursor.execute(
                f"SELECT * FROM commission;"
            )
            return cursor.fetchone()


class AdminSetDB(Database):
    logger = logging.getLogger("bot.data.admin_set_db")

    def admin_add(self, user_id: int, username, first_name, last_name):
        self.logger.info('Админ добавляет себя в БД')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO admins (user_id, username, first_name, last_name) "
                "VALUES (%(user_id)s, %(username)s, %(first_name)s, %(last_name)s);", {
                    'user_id': user_id,
                    'username': username,
                    'first_name': first_name,
                    'last_name': last_name,
                }
            )
            self.connection.commit()

    def admin_set_commission_for_performer(self, performer):
        self.logger.info('Админ устанавливает комиссию для Исполнителя')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "UPDATE commission SET performer = %(performer)s;", {
                    'performer': performer,
                }
            )
            self.connection.commit()

    def admin_set_commission_for_customer(self, customer):
        self.logger.info('Админ устанавливает комиссию для Заказчика')
        with self.connection.cursor() as cursor:
            cursor.execute(
                "UPDATE commission SET customer = %(customer)s;", {
                    'customer': customer,
                }
            )
            self.connection.commit()

    def admin_set_commission_for_categories(self, category, commission):
        self.logger.info(f'Админ устанавливает комиссию для {category} в размере {commission}')
        with self.connection.cursor() as cursor:
            cursor.execute(
                f"UPDATE commission SET {category} = %(commission)s;", {
                    'commission': commission,
                }
            )
            self.connection.commit()

    def admin_set_money(self, type_user, user_id, money):
        self.logger.info(f'Админ добавляет деньги {money} для {type_user}')
        with self.connection.cursor() as cursor:
            cursor.execute(
                f"UPDATE {type_user} SET {type_user[0:-1]}_money = {type_user[0:-1]}_money + %(money)s "
                "WHERE user_id = %(user_id)s;", {
                    'user_id': user_id,
                    'money': money,
                }
            )
            self.connection.commit()


admin_set_db_obj = AdminSetDB()
admin_get_db_obj = AdminGetDB()
performer_set_db_obj = PerformerSetDB()
performer_get_db_obj = PerformerGetDB()
customer_set_db_obj = CustomerSetDB()
customer_get_db_obj = CustomerGetDB()
global_set_db_obj = GlobalSetDB()
global_db_obj = GlobalGetDB()
