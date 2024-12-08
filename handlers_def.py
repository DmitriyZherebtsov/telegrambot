
import time
import telebot
from telebot import types
import psycopg2
import config
import logging
logging.basicConfig(level=logging.INFO, filename=config.log_path, filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s")
bot = telebot.TeleBot(config.telebot_token)

def menu(message_chat_id):
    logging.debug("start func 'menu'")
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("Внесите ДР", callback_data='add bd')
    btn2 = types.InlineKeyboardButton("Показать список ДР", callback_data='show bd')
    btn3 = types.InlineKeyboardButton("Изменить запись", callback_data='change_info')
    btntime = types.InlineKeyboardButton("Время отправки", callback_data='choose_time')
    btn_review = types.InlineKeyboardButton("Оставить отзыв", callback_data='review')
    markup.add(btn1).add(btn2).add(btn3).add(btntime).add(btn_review)
    bot.send_message(message_chat_id, 'Выберите действие:', reply_markup=markup)
def add_feedback(message):
    logging.debug("start func 'add_feedback'")
    try:
        logging.info("connect to db ('add_feedback')")
        connection = psycopg2.connect(dbname = config.db_name, user= config.db_user)
        cur = connection.cursor()
        cur.execute("INSERT INTO memento.review(chat_id, review) VALUES ('%s', '%s')" % (
        message.chat.id, message.text.strip()))
        logging.info("inserting users' review ('add_feedback')")
        connection.commit()
        cur.close()
        connection.close()
        bot.send_message(message.chat.id, 'Спасибо за Ваш отзыв!')
        menu(message.chat.id)
    except Exception:
        logging.error("smth went wrong", exc_info=True)
        bot.send_message(message.chat.id, 'Что-то пошло не так:(')
        menu(message.chat.id)

def change_time(message):
            #TODO: проверить формат времени (:)
    logging.debug("start func 'chande_time'")
    try:
        time.strptime(message.text.strip(), '%H:%M')
        logging.info("connect to db ('change_time')")
        connection = psycopg2.connect(dbname = config.db_name, user= config.db_user)
        cur = connection.cursor()
        cur.execute("UPDATE memento.send_time SET update_dt = current_timestamp, time = '%s'  WHERE chat_id ='%s' " % (
        message.text.strip(), message.chat.id))
        connection.commit()
        cur.close()
        connection.close()
        bot.send_message(message.chat.id, 'Время изменено успешно')
        logging.info("time was changed successfully ('change_time')")
        menu(message.chat.id)
    except ValueError:
        logging.error("wrong data or format", exc_info=True)
        bot.send_message(message.chat.id, 'Что-то пошло не так. Попробуйте другие данные.')
        menu(message.chat.id)

