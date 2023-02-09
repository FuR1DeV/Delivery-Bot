import os
from dotenv import load_dotenv
from emoji import emojize
from pyqiwip2p import QiwiP2P
from urllib.parse import quote

load_dotenv()

VERSION = '0.0.1'
AUTHOR = 'Vasiliy Turtugeshev'

HOST = os.getenv('HOST')
POSTGRESQL_USER = os.getenv('POSTGRESQL_USER')
POSTGRESQL_PASSWORD = os.getenv('POSTGRESQL_PASSWORD')
DATABASE = os.getenv('DATABASE')

POSTGRES_URI = f"postgresql://{POSTGRESQL_USER}:" \
                    f"%s@{HOST}/{DATABASE}" % quote(f"{POSTGRESQL_PASSWORD}")

BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = str(os.getenv('ADMIN_ID')).split(',')
P2P = QiwiP2P(auth_key=os.getenv('QIWI_PRIVATE_KEY'))

COUNT = 0

PRIVATE_CHAT_LINK = 'http://t.me/+CLLM8RBkM2o2YzIy'

KEYBOARD = {
    'DASH': emojize(':minus:'),
    'PLUS': emojize(':plus:'),
    'SUN': emojize(':sun:'),
    'ROCKET': emojize(':rocket:'),
    'AIRPLANE': emojize(':airplane:'),
    'RACING_CAR': emojize(':racing_car:'),
    'TRACTOR': emojize(':tractor:'),
    'TWELVE_O’CLOCK': emojize(':twelve_o’clock:'),
    'THUMBS_UP': emojize(':thumbs_up:'),
    'THUMBS_DOWN': emojize(':thumbs_down:'),
    'SMILING_FACE_WITH_SUNGLASSES': emojize(':smiling_face_with_sunglasses:'),
    'BUST_IN_SILHOUETTE': emojize(':bust_in_silhouette:'),
    'BUSTS_IN_SILHOUETTE': emojize(':busts_in_silhouette:'),
    'HOUSE': emojize(':house:'),
    'BOUQUET': emojize(':bouquet:'),
    'WRAPPED_GIFT': emojize(':wrapped_gift:'),
    'SHORTCAKE': emojize(':shortcake:'),
    'STOPWATCH': emojize(':stopwatch:'),
    'PAGE_WITH_WITH_CURL': emojize(':page_with_curl:'),
    'ARROWS_BUTTON': emojize(':counterclockwise_arrows_button:'),
    'HAMMER_AND_PICK': emojize(':hammer_and_pick:'),
    'RECYCLING_SYMBOL': emojize(':recycling_symbol:'),
    'SOS_BUTTON': emojize(':SOS_button:'),
    'MONEY_BAG': emojize(':money_bag:'),
    'OUTBOX_TRAY': emojize(':outbox_tray:'),
    'INBOX_TRAY': emojize(':inbox_tray:'),
    'ON!_ARROW': emojize(':ON!_arrow:'),
    'EX_QUEST_MARK': emojize(':exclamation_question_mark:'),
    'PENCIL': emojize(':pencil:'),
    'DOLLAR': emojize(':dollar_banknote:'),
    'ID_BUTTON': emojize(':ID_button:'),
    'CLIPBOARD': emojize(':clipboard:'),
    'INFORMATION': emojize(':information:'),
    'AUTOMOBILE': emojize(':automobile:'),
    'PERSON_RUNNING': emojize(':person_running:'),
    'WRENCH': emojize(':wrench:'),
    'WORLD_MAP': emojize(':world_map:'),
    'WRITING_HAND': emojize(':writing_hand:'),
    'GLOBE_WITH_MERIDIANS': emojize(':globe_with_meridians:'),
    'BAR_CHART': emojize(':bar_chart:'),
    'DOWNWARDS_BUTTON': emojize(':downwards_button:'),
    'UPWARDS_BUTTON': emojize(':upwards_button:'),
    'CROSS_MARK': emojize(':cross_mark:'),
    'CHECK_MARK_BUTTON': emojize(':check_mark_button:'),
    'CHECK_BOX_WITH_CHECK': emojize(':check_box_with_check:'),
    'TELEPHONE': emojize(':telephone_receiver:'),
    'COMP': emojize(':desktop_computer:'),
    'PHONE': emojize(':mobile_phone:'),
    'GREEN_CIRCLE': emojize(':green_circle:'),
    'RED_CIRCLE': emojize(':red_circle:'),
    'BLUE_CIRCLE': emojize(':blue_circle:'),
    'WHITE_CIRCLE': emojize(':white_circle:'),
    'A_BUTTON': emojize(':A_button_(blood_type):'),
    'B_BUTTON': emojize(':B_button_(blood_type):'),
    'KICK_SCOOTER': emojize(':kick_scooter:'),
    'INPUT_LATIN_LETTERS': emojize(':input_latin_letters:'),
    'WAVING_HAND': emojize(':waving_hand:'),
    'STAR': emojize(':star:'),
    'GLOWING_STAR': emojize(':glowing_star:'),
    'RIGHT_ARROW_CURVING_LEFT': emojize(':right_arrow_curving_left:'),
}
