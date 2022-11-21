# !Delivery Bot

Telegram bot for delivery
------------------------------------

### pip
##### pip install aiogram
##### pip install requests
##### pip install python-dotenv
##### pip install emoji
##### pip install psycopg2
##### pip install geopy
##### pip install pyqiwip2p
##### pip install aioschedule

### Description
##### Создаём файл .env, куда вписываем хост (HOST), имя юзера бд(POSTGRESQL_USER), пароль от бд (POSTGRESQL_PASSWORD) и название бд (DATABASE) токен бота (BOT_TOKEN) а так же ADMIN_ID в таком виде id, сейчас вписан айди разработчика этого бота
  HOST=""  
  POSTGRESQL_USER=""  
  POSTGRESQL_PASSWORD=""  
  DATABASE=""  
  BOT_TOKEN=""  
  ADMIN_ID="351490585,"  
  QIWI_PRIVATE_KEY=""


##### - Qiwi Private Key - Свой ключ должен ввести владелец бота. Ниже ссылка на инструкцию как создать свой приватный ключ


https://developer.qiwi.com/ru/p2p-payments/#p2p-


##### - Выгрузка файлов csv находится в папке logs, вместе с логами

##### - Запуск основного бота, производится путём запуска main.py

##### - Команда /start для пользователей.

##### - Команда /admin для админов.
