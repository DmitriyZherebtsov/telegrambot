
import time
import telebot
from telebot import types
import psycopg2
import config
bot = telebot.TeleBot(config.telebot_token)

def menu(message_chat_id):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("Внесите ДР", callback_data='add bd')
    btn2 = types.InlineKeyboardButton("Показать список ДР", callback_data='show bd')
    btn3 = types.InlineKeyboardButton("Изменить запись", callback_data='change_info')
    btntime = types.InlineKeyboardButton("Время отправки", callback_data='choose_time')
    btn_review = types.InlineKeyboardButton("Оставить отзыв", callback_data='review')
    markup.add(btn1).add(btn2).add(btn3).add(btntime).add(btn_review)
    bot.send_message(message_chat_id, 'Выберите действие:', reply_markup=markup)
def action(message: types.Message):
    menu(message.chat.id)
def add_feedback(message):
    try:
        connection = psycopg2.connect(dbname = config.db_name, user= config.db_user)
        cur = connection.cursor()
        cur.execute("INSERT INTO memento.review(chat_id, review) VALUES ('%s', '%s')" % (
        message.chat.id, message.text.strip()))
        connection.commit()
        cur.close()
        connection.close()
        bot.send_message(message.chat.id, 'Спасибо за Ваш отзыв!')
        action(message)
    except Exception:
        bot.send_message(message.chat.id, 'Что-то пошло не так:(')
        action(message)

def change_time(message):
            #TODO: проверить формат времени (:)
    try:
        time.strptime(message.text.strip(), '%H:%M')
        connection = psycopg2.connect(dbname = config.db_name, user= config.db_user)
        cur = connection.cursor()
        cur.execute("UPDATE memento.send_time SET update_dt = current_timestamp, time = '%s'  WHERE chat_id ='%s' " % (
        message.text.strip(), message.chat.id))
        connection.commit()
        cur.close()
        connection.close()
        bot.send_message(message.chat.id, 'Время изменено успешно')
        action(message)
    except ValueError:
        bot.send_message(message.chat.id, 'Что-то пошло не так. Попробуйте другие данные.')
        action(message)

