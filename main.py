# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import telebot
from telebot import types
import sqlite3
bot = telebot.TeleBot('6827864691:AAH2MPjAwSdaQctyiic5Z2Nbo30AQ8rxMl8')
date_of_bd = None
name = None
class User:
    def __init__(self, name):
        self.name = name
@bot.message_handler(commands=['start','hello'])
def start(message):
    connection = sqlite3.connect('bd.sql')
    cur = connection.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS users(name varchar(100), date_of_bd date)')
    connection.commit()
    cur.close()
    connection.close()
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("Внесите ДР", callback_data='add bd')
    markup.add(btn1)
    bot.send_message(message.chat.id,'Здравствуйте, повелитель!', reply_markup=markup)
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
            cur.execute("INSERT INTO users(name, date_of_bd) VALUES ('%s', '%s')" % (name, date_of_bd))
            connection.commit()
            cur.close()
            connection.close()
            msg = bot.reply_to(message, 'Добавлен пользователь: ' + user.name)
            #bot.register_next_step_handler(msg, )
bot.infinity_polling()

'''
def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

'''