import telebot
from telebot import types

from google_sheets import get_total_revenue, add_row
from settings import TG_TOKEN, SHEET_URL
from utils import create_batton

bot = telebot.TeleBot(TG_TOKEN, parse_mode=None) #TG_TOKEN из файла settings

BTN_DOC = create_batton('doc', '📝 Показать документ')
BTN_REV = create_batton('rev','💲 Общая выручка')
BTN_NEW_ITEM = create_batton('new_item', '✅ Добавить продажу')
BTN_CANCEL = create_batton('cancel', '❌ Отмена')

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

    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton(BTN_DOC['text'], callback_data=BTN_DOC['key'])
    btn2 = types.InlineKeyboardButton(BTN_REV['text'], callback_data=BTN_REV['key'])
    btn3 = types.InlineKeyboardButton(BTN_CANCEL['text'], callback_data=BTN_CANCEL['key'])
    markup.add(btn1, btn2, btn3)

    bot.send_message(message.chat.id, 'Спасибо 👍. Я добавил в отчет новую продажу.',
                     reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        if call.data == BTN_DOC['key']:
            bot.send_message(call.message.chat.id,
                             f'<a href="{SHEET_URL}">Отчёт по продажам</a>',
                             parse_mode='html')
        elif call.data == BTN_REV['key']:
            bot.send_message(call.message.chat.id,
                             f'Общая выручка = <b>{get_total_revenue()}</b>',
                             parse_mode='html')
        elif call.data == BTN_CANCEL['key']:
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  text="OK 👌",
                                  reply_markup=None)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):  #Функция приветственного сообщения
    img = open('start.jpg', 'rb') #приветственная картинка
    bot.send_sticker(message.chat.id, img) #выводит приветственную картинку

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton(BTN_DOC['text'])
    btn2 = types.KeyboardButton(BTN_REV['text'])
    btn3 = types.KeyboardButton(BTN_NEW_ITEM['text'])
    markup.add(btn1, btn2, btn3)
#Метод reply_to отвечает на сообщение. Мы предаем 2 параметра в этот метод: сообщение отправленное пользователем, на которое нужно ответить и текст нашего сообщения:
    bot.reply_to(message, "Привет! Это Ваш личный помошник. Чего изволите?", reply_markup=markup)

#Функция, которая реагирует на нажатие кнопок и передаёт ответы по условиям
@bot.message_handler(content_types=['text']) #оборачиваем функцию send_text в декоратор message_handler, но в данном случае мы передаем параметр content_types, который содержит тип текст.
# Это значит, что наша собственная функция send_text будет срабатывать, когда в бот будет отправлено любое текстовое сообщение.
def send_text(message): #Функция реагирует на нажатие кнопок
#В теле самой функции мы проверяем чему равен текст сообщения - какая нажата кнопка?
# Если он равен '📝 Показать документ', то вызываем метод бота send_message. Метод send_message отправляет сообщение.
# Первый параметр метода - ID чата. Второй параметр - текст самого сообщения. Третий параметр parse_mode (опциональный) - режим парсинга сообщения
    if message.text == BTN_DOC['text']:
        bot.send_message(message.chat.id, f'<a href="{SHEET_URL}">Отчёт по продажам</a>', #Выводит ссылку на файл-таблицу в Google Sheet
                         parse_mode='html')
    elif message.text == BTN_REV['text']:
        bot.send_message(message.chat.id,
                         f'Общая выручка = <b>{get_total_revenue()}</b>', #Выводит сумму Общая выручка по функции get_total_revenue
                         parse_mode='html')
    elif message.text == BTN_NEW_ITEM['text']:
        add_new_item(message)
