# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import telebot
from telebot import types
bot = telebot.TeleBot('6827864691:AAH2MPjAwSdaQctyiic5Z2Nbo30AQ8rxMl8')
date_of_bd = ''
name_surname = ''
@bot.message_handler(commands=['start','hello'])

def main(message):
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
            date_of_bd = message.text
        if len(date_of_bd)>0:
            @bot.message_handler(content_types=['text'])
            bot.send_message(callback.message.chat.id, 'Введите имя и фамилию')
            def handle_name(message):
                global name_surname
                name_surname = message.text
    bot.send_message(callback.message.chat.id, date_of_bd + name_surname)
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