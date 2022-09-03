import telebot
from telebot import types

from google_sheets import get_total_revenue, add_row
from settings import TG_TOKEN, SHEET_URL
from utils import create_batton

bot = telebot.TeleBot(TG_TOKEN, parse_mode=None)

BTN_DOC = create_batton('doc', '📝 Показать документ')
BTN_REV = create_batton('rev','💲 Общая выручка')
BTN_NEW_ITEM = create_batton('new_item', '✅ Добавить продажу')

def add_new_item(message):
    new_item = [message.from_user.first_name]
    msg = bot.send_message(message.chat.id, 'Введите объект')
    bot.register_next_step_handler(msg, add_title, new_item=new_item)

def add_title(message, **kwargs):
    new_item = kwargs.get('new_item', [])
    new_item.append(message.text)
    msg = bot.send_message(message.chat.id, 'Введите сумму выручки')
    bot.register_next_step_handler(msg, add_revenue, new_item=new_item)

def add_revenue(message, **kwargs):
    new_item = kwargs.get('new_item', [])
    new_item.append(message.text)
    add_row(new_item)
    bot.send_message(message.chat.id, 'Спасибо 👍. Я добавил в отчет новую продажу.')

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    img = open('start.jpg', 'rb')
    bot.send_sticker(message.chat.id, img)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton(BTN_DOC['text'])
    btn2 = types.KeyboardButton(BTN_REV['text'])
    btn3 = types.KeyboardButton(BTN_NEW_ITEM['text'])
    markup.add(btn1, btn2, btn3)

    bot.reply_to(message, "Привет! Это твой личный помошник. Чего изволите?", reply_markup=markup)


@bot.message_handler(content_types=['text'])
def send_text(message):
    if message.text == BTN_DOC['text']:
        bot.send_message(message.chat.id, f'<a href="{SHEET_URL}">Отчёт по продажам</a>',
                         parse_mode='html')
    elif message.text == BTN_REV['text']:
        bot.send_message(message.chat.id,
                         f'Общая выручка = <b>{get_total_revenue()}</b>',
                         parse_mode='html')
    elif message.text == BTN_NEW_ITEM['text']:
        add_new_item(message)
