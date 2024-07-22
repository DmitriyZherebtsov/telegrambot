import psycopg2
import schedule
import re
import time
import datetime
from threading import Thread
from time import sleep
import telebot
from telebot import types
import psycopg2
bot = telebot.TeleBot('6827864691:AAH2MPjAwSdaQctyiic5Z2Nbo30AQ8rxMl8')
def action(message: types.Message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("Внесите ДР", callback_data='add bd')
    btn2 = types.InlineKeyboardButton("Показать список ДР", callback_data='show bd')
    btn3 = types.InlineKeyboardButton("Изменить запись", callback_data='change_info')
    btntime = types.InlineKeyboardButton("Время отправки", callback_data='choose_time')
    btn_review = types.InlineKeyboardButton("Оставить отзыв", callback_data='review')
    markup.add(btn1).add(btn2).add(btn3).add(btntime).add(btn_review)
    global user_id_tg
    bot.send_message(message.chat.id, 'Выберите действие:', reply_markup=markup)
def add_feedback(message):
    try:
        connection = psycopg2.connect(dbname='polluvna', user='polluvna', password='KyFPza0pFLM7',
                                          host='158.160.137.15')
        cur = connection.cursor()
        cur.execute("INSERT INTO public.review(chat_id, review) VALUES ('%s', '%s')" % (
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
        connection = psycopg2.connect(dbname='polluvna', user='polluvna', password='KyFPza0pFLM7',
                                              host='158.160.137.15')
        cur = connection.cursor()
        cur.execute("UPDATE public.send_time SET update_dt = current_timestamp, time = '%s'  WHERE chat_id ='%s' " % (
        message.text.strip(), message.chat.id))
        connection.commit()
        cur.close()
        connection.close()
        bot.send_message(message.chat.id, 'Время изменено успешно')
        action(message)
    except ValueError:
        bot.send_message(message.chat.id, 'Что-то пошло не так. Попробуйте другие данные.')
        action(message)

