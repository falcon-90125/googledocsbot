import telebot
from telebot import types

from google_sheets import get_total_revenue, add_row
from settings import TG_TOKEN, SHEET_URL
from utils import create_batton
#Объект - бот
bot = telebot.TeleBot(TG_TOKEN, parse_mode=None) #TG_TOKEN из файла settings
# Best Practis: если мы делаем что-то одинаковое несколько раз, то от него нужно избавляться
#создаём кнопки функцией общего назначения create_batton из файла utils, чтобы не дублировать один и тот же код в разных местах.
BTN_DOC = create_batton('doc', '📝 Показать документ')
BTN_REV = create_batton('rev','💲 Общая выручка')
BTN_NEW_ITEM = create_batton('new_item', '✅ Добавить продажу')
BTN_CANCEL = create_batton('cancel', '❌ Закрыть inline-клавиатуру')

#Функция добавления новой продажи
def add_new_item(message): #Принимает объект сообщения
    new_item = [message.from_user.first_name] #сначала формирует список значений, где первым значением будет first_name user'а - отправителя сообщения
    msg = bot.send_message(message.chat.id, 'Введите объект') #бот отправляет сообщение 'Введите объект', а результатом метода send_message будет сообщение, которое напишет user, сохраняем его в msg
    bot.register_next_step_handler(msg, add_title, new_item=new_item) #Метод bot.register_next_step_handler работатет с последовательностью шагов, который регистрирует следующий шаг обработчика.
    #Он будет ждать от user'а сообщение, как только он его отправит, запустится функция add_title (см.ниже), таким образом метод bot.register_next_step_handler принимает сообщение user'а, при его получении
    #запускает функцию add_title, и записывает в произвольный параметр new_item список new_item, в который далее будут добавлятся данные

#Функция добавления названия объекта
def add_title(message, **kwargs): #Принимает объект сообщения и kwargs - все произвольные параметры, кот. мы указываем в методе bot.register_next_step_handler предыдущей функции - new_item
    new_item = kwargs.get('new_item', []) #Получаем список new_item, кот. был сформирован в def add_new_item
    new_item.append(message.text) #Затем добавляем текст из сообщения user'а - введённое название объекта в ответ на 'Введите объект' в функции add_new_item
    msg = bot.send_message(message.chat.id, 'Введите сумму выручки') #бот отправляет сообщение 'Введите сумму выручки', а результатом метода send_message будет сообщение, которое напишет user, сохраняем его в msg
    bot.register_next_step_handler(msg, add_revenue, new_item=new_item) #запустится функция add_revenue (см.ниже), таким образом метод bot.register_next_step_handler принимает сообщение user'а, при его получении
    #запускает функцию add_revenue, и записывает в произвольный параметр new_item список new_item, в который далее будут добавлятся данные

#Функция добавления Суммы выручки
def add_revenue(message, **kwargs): #Принимает объект сообщения и kwargs - все произвольные параметры, кот. мы указываем в методе bot.register_next_step_handler предыдущей функции - new_item
    new_item = kwargs.get('new_item', []) #Получаем список new_item, кот. был сформирован в def add_title
    new_item.append(message.text) #Затем добавляем текст из сообщения user'а - введённую сусмму выручки в ответ на 'Введите сумму выручки' в функции add_title
    add_row(new_item) #Далее список обрабатывается данной функцией из модуля(файла) google_sheets - данные списка добавляются в таблицу на Google Sheets
    #Вызов inline-клавиатуры после добавления новой продажи
    markup = types.InlineKeyboardMarkup(row_width=2) #параметр row_width - кол-во кнопок в ряд
    btn1 = types.InlineKeyboardButton(BTN_DOC['text'], callback_data=BTN_DOC['key'])  #callback_data(данные ответа) - это то значение (ключ словаря кнопки), кот. будет передано в объект сообщения, когда user нажмёт кнопку,
    btn2 = types.InlineKeyboardButton(BTN_REV['text'], callback_data=BTN_REV['key'])      #это сообщение будет обработано функцией send_text (самая нижняя)
    btn3 = types.InlineKeyboardButton(BTN_CANCEL['text'], callback_data=BTN_CANCEL['key'])
    markup.add(btn1, btn2, btn3)

    bot.send_message(message.chat.id, 'Спасибо 👍. Я добавил в отчет новую продажу.',
                     reply_markup=markup) #в reply_markup передаём созданую inline-клавиатуру

 #Функция обработки нажатий кнопок на inline-клавиатуре
@bot.callback_query_handler(func=lambda call: True) #срабатывает при нажатий кнопок на inline-клавиатуре, т.е. если в callback_data inline-клавиатуры передан ключ словаря кнопки - это call: True
def callback_inline(call): #принимает параметр call, в который передаётся значение callback_data из вызова inline-клавиатуры
    if call.message:
        if call.data == BTN_DOC['key']: #если нажата кнопка "Показать документ"
            bot.send_message(call.message.chat.id,
                             f'<a href="{SHEET_URL}">Отчёт по продажам</a>', #показываем ссылку на документ
                             parse_mode='html')
        elif call.data == BTN_REV['key']: #если нажата кнопка "Общая выручка"
            bot.send_message(call.message.chat.id,
                             f'Общая выручка = <b>{get_total_revenue()}</b>', #выводит сообщение о выручке
                             parse_mode='html')
        elif call.data == BTN_CANCEL['key']: #если нажата кнопка "Отмена",
            bot.edit_message_text(chat_id=call.message.chat.id, #то методом edit_message_text меняем отправленное сообщение из функции add_revenue на то что указано в параметре "text" ниже
                                  message_id=call.message.message_id,
                                  text="OK 👌", #новый текст или можно оставлять предыдущий текст из функции add_revenu "Спасибо 👍. Я добавил в отчет новую продажу."
                                  reply_markup=None)  #удалить inline-клавиатуру

 #Функция приветственного сообщения
@bot.message_handler(commands=['start', 'help']) #оборачиваем функцию send_welcome в декоратор message_handler(обработчик сообщений),
#в кот. мы передаем параметр commands, кот. содержит тип текст.
def send_welcome(message):
    img = open('start.jpg', 'rb') #приветственная картинка
    bot.send_sticker(message.chat.id, img) #выводит приветственную картинку

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True) #выводит панель с кнопками
    btn1 = types.KeyboardButton(BTN_DOC['text'])
    btn2 = types.KeyboardButton(BTN_REV['text'])
    btn3 = types.KeyboardButton(BTN_NEW_ITEM['text'])
    markup.add(btn1, btn2, btn3)
#Метод reply_to отвечает на сообщение. Мы предаем 2 параметра в этот метод: сообщение отправленное пользователем, на которое нужно ответить и текст нашего сообщения:
    bot.reply_to(message, "Привет! Это Ваш личный помошник. Чего изволите?", reply_markup=markup)

#Функция, которая реагирует на нажатие кнопок и передаёт ответы по условиям
@bot.message_handler(content_types=['text']) #оборачиваем функцию send_text в декоратор message_handler(обработчик сообщений),
# но в данном случае мы передаем параметр content_types, кот. содержит тип текст (ключ словаря кнопки).
# Это значит, что наша собственная функция send_text будет срабатывать, когда в бот будет отправлено любое текстовое сообщение.
def send_text(message): #Функция реагирует на нажатие кнопок
#В теле самой функции мы проверяем чему равен текст сообщения - какая нажата кнопка?
# Если он равен '📝 Показать документ', то вызываем метод бота send_message. Метод send_message отправляет сообщение.
# Первый параметр метода - ID чата. Второй параметр - текст самого сообщения. Третий параметр parse_mode (опциональный) - режим парсинга сообщения
    if message.text == BTN_DOC['text']: #срабатывает если сообщение равно ключу словаря этой кнопки
        bot.send_message(message.chat.id, f'<a href="{SHEET_URL}">Отчёт по продажам</a>', #Выводит текстовую ссылку "Отчёт по продажам" на файл-таблицу в Google Sheet
                         parse_mode='html')
    elif message.text == BTN_REV['text']: #срабатывает если сообщение равно ключу словаря этой кнопки
        bot.send_message(message.chat.id,
                         f'Общая выручка = <b>{get_total_revenue()}</b>', #Выводит сумму Общая выручка по функции get_total_revenue
                         parse_mode='html')
    elif message.text == BTN_NEW_ITEM['text']: #срабатывает если сообщение равно ключу словаря этой кнопки
        add_new_item(message) #Обрабатывает функции добавления новой продажи в таблицу на Google Sheets: имя user'а, названия объекта и суммы выручки

