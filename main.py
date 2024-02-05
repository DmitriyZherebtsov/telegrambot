# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import telebot
from telebot import types
bot = telebot.TeleBot('6827864691:AAH2MPjAwSdaQctyiic5Z2Nbo30AQ8rxMl8')
date_of_bd = None
user_id_tg = None
name = None
phone = None
email = None
information = None
message_chat_id = None
import psycopg2
connection = psycopg2.connect(dbname='postgres', user='postgres', password='postgres', host='158.160.146.175')
cur = connection.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS users(name varchar(100), date_of_bd date(100), user_id varchar(100), phone varchar(100), email varchar(100), information varchar(200))')
cur.close()
connection.close()
@bot.message_handler(commands=['start','hello'])
def start(message):
    global user_id_tg
    user_id_tg = message.from_user.id
    bot.send_message(message.chat.id,'Здравствуйте, повелитель!')
    global message_chat_id
    message_chat_id = message.chat.id
    action(message_chat_id)
def action(message_chat_id):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("Внесите ДР", callback_data='add bd')
    btn2 = types.InlineKeyboardButton("Показать список ДР", callback_data='show bd')
    markup.add(btn1, btn2)
    bot.send_message(message_chat_id, 'Выберите действие:', reply_markup=markup)

@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    if callback.data == 'add bd':
        bot.send_message(callback.message.chat.id, 'Введите дату в формате дд.мм.гггг')
        @bot.message_handler(content_types=['text'])
        def handle_bd(message):
            global date_of_bd
            date_of_bd = message.text.strip()
            msg = bot.reply_to(message, 'Введите имя и фамилию')
            bot.register_next_step_handler(msg, process_name)
        def process_name(message):
            global name
            name = message.text.strip()
            msg = bot.reply_to(message, 'Введите номер телефона')
            bot.register_next_step_handler(msg, process_phone)
        def process_phone(message):
            global phone
            phone = message.text.strip()
            msg = bot.reply_to(message, 'Введите почту')
            bot.register_next_step_handler(msg, process_email)
        def process_email(message):
            global email
            email = message.text.strip()
            msg = bot.reply_to(message, 'Введите краткую информацию о человеке')
            bot.register_next_step_handler(msg, process_information)
        def process_information(message):
            global information
            global name
            global date_of_bd
            global phone
            global email
            information = message.text.strip()
            connection = psycopg2.connect('postgres')
            cur = connection.cursor()
            cur.execute("INSERT INTO users(name, date_of_bd, user_id, phone, email, information) VALUES ('%s', '%s', '%s', '%s', '%s', '%s')" % (name, date_of_bd, user_id_tg, phone, email, information))
            cur.close()
            connection.close()
            bot.reply_to(message, 'Добавлен пользователь: ' + name)
            action(message_chat_id)
    if callback.data == 'show bd':
        connection = psycopg2.connect('postgres')
        cur = connection.cursor()
        connection.commit()
        cur.execute("SELECT name, date_of_bd FROM Users where user_id ='%s' " % (user_id_tg))
        users = cur.fetchall()

        # Выводим результаты
        for user in users:
            s = ' '
            for name in user:
                s = s + ' ' + name
            s = s + '\n'
            bot.send_message(callback.message.chat.id, s)

        # Закрываем соединение
        cur.close()
        connection.close()
        action(message_chat_id)

bot.infinity_polling()

