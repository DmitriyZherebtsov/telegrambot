# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import telebot
from telebot import types
import sqlite3
bot = telebot.TeleBot('6827864691:AAH2MPjAwSdaQctyiic5Z2Nbo30AQ8rxMl8')
date_of_bd = None
user_id_tg = None
name = None

connection = sqlite3.connect('bd.sql')
cur = connection.cursor()
#cur.execute('drop table users')
cur.execute('CREATE TABLE IF NOT EXISTS users(name varchar(100), date_of_bd varchar(100), user_id varchar(100))')
connection.commit()
cur.close()
connection.close()

#action(message)

class User:
    def __init__(self, name):
        self.name = name

@bot.message_handler(commands=['start','hello'])
def start(message):
    global user_id_tg
    user_id_tg = message.from_user.id
    bot.send_message(message.chat.id,'Здравствуйте, повелитель!')
    action(message)
def action(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("Внесите ДР", callback_data='add bd')
    btn2 = types.InlineKeyboardButton("Показать список ДР", callback_data='show bd')
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, 'Выберите действие:', reply_markup=markup)

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
            user = User(name)
            connection = sqlite3.connect('bd.sql')
            cur = connection.cursor()
            cur.execute("INSERT INTO users(name, date_of_bd, user_id) VALUES ('%s', '%s', '%s')" % (name, date_of_bd, user_id_tg))
            connection.commit()
            cur.close()
            connection.close()
            bot.reply_to(message, 'Добавлен пользователь: ' + user.name)
            action(message)
    if callback.data == 'show bd':
        connection = sqlite3.connect('bd.sql')
        cur = connection.cursor()
        connection.commit()
        cur.execute("SELECT * FROM Users where user_id ='%s' " % (user_id_tg))
        users = cur.fetchall()

        # Выводим результаты
        for user in users:
            bot.send_message(callback.message.chat.id, user[0] + ' ' + user[1])

        # Закрываем соединение
        cur.close()
        connection.close()


bot.infinity_polling()

