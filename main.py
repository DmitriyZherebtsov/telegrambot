# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import schedule
import re
import datetime
from threading import Thread
import time
from time import sleep
import telebot
from telebot import types
import psycopg2
import handlers_def
import gpt_def
import logging
import config
def schedule_checker():
    while True:
        schedule.run_pending()
        sleep(1)
def function_to_run():
    try:
        connection = psycopg2.connect(dbname = config.db_name, user= config.db_user)
        curs = connection.cursor()
        curs.execute(" SELECT u.name, cast(date_part('year', age(u.date_of_bd)) as text), u.information, st.chat_id FROM memento.send_time st JOIN memento.users u ON u.chat_id = st.chat_id where extract(day from u.date_of_bd) = extract(day from current_timestamp) and extract(month from u.date_of_bd) = extract(month from current_timestamp) and extract(hour from to_timestamp(st.time,'HH24:MI')) = extract(hour from current_timestamp) and extract(minute from to_timestamp(st.time,'HH24:MI')) = extract(minute from current_timestamp) ")
        users1 = curs.fetchall()
        for user in users1:
            bot.send_message(user[3], gpt_def.conn_gpt(user))
        curs.close()
        connection.close()
        handlers_def.menu(user[3])
    except Exception:
        bot.send_message(user[3], 'Что-то пошло не так при попытке похода в базу. ')
        handlers_def.menu(user[3])

bot = telebot.TeleBot(config.telebot_token)
date_of_bd = None
chat_id_tg = None
name = None
phone = None
email = None
information = None
message_chat_id = None
list_for_update = []
list_of_inserts = {} #словарь для вставок пользователей. 1 пользователь = 1 запись
try:
    connection = psycopg2.connect(dbname = config.db_name, user= config.db_user)
    cur = connection.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS memento.users(name varchar(100), date_of_bd date, chat_id varchar(100), phone varchar(100), email varchar(100), information varchar(200), id serial4 PRIMARY KEY, update_dt date default current_timestamp)')
    cur.execute('CREATE TABLE IF NOT EXISTS memento.send_time(name varchar (100), time varchar(50), chat_id varchar(100), update_dt date default current_timestamp)')
    cur.execute('CREATE TABLE IF NOT EXISTS memento.review(chat_id varchar(100), review varchar(1000), update_dt date default current_timestamp)')
    connection.commit()
    cur.close()
    connection.close()
except Exception:
    print('Не удалось подключиться к базе')
@bot.message_handler(commands=['start','hello'])
def start(message):
    #TODO: сделать приветственное сообщение (функционал бота, пожертвования и тд)
    try:
        connection = psycopg2.connect(dbname = config.db_name, user= config.db_user)
        cur = connection.cursor()
        cur.execute("SELECT chat_id FROM memento.send_time")
        send_time_chat_ids = cur.fetchall()
        chat_id_array = []
        for chat_ids in send_time_chat_ids:
            chat_id_array.append(chat_ids[0])
        if str(message.chat.id) not in chat_id_array:
            cur.execute(
                "INSERT INTO memento.send_time(time, chat_id) VALUES ('%s', '%s')" % ('9:00', message.chat.id))
        connection.commit()
        cur.close()
        connection.close()
        to_pin = bot.send_message(message.chat.id,'Привет! \n'
            'Это бот, который напомнит тебе о днях рождениях твоих близких и подготовит поздравления для них 🥰 \n'
            
            '\n Пользоваться нашим ботом крайне просто: вы вносите дату рождения, имя, контактную информацию (при необходимости) и небольшой комментарий. \n'
            '\n В день рождения вашего близкого человека наш бот пришлёт вам уведомление и подготовит небольшое поздравление, используя ваш комментарий :) \n'
            
            '\n В качестве удобства использования этого бота, вы можете выбрать наиболее подходящее время напоминаний. По умолчанию это время 9:00 утра. Однако вы можете его поменять, нажав кнопку "Время отправки". \n'
            
            '\n Если вы хотите нас отблагодарить, поддержать работу и продвижение нашего бота, вы можете' "<a href='https://www.tinkoff.ru/cf/7L9dLH3LWHr'> перевести </a>" 'нам любую комфортную сумму \n'
            '\n Создатели: \n'
            '@poluvna \n'
            '@Dmitry_Zherebtsov', parse_mode = "HTML").message_id
        bot.pin_chat_message(chat_id=message.chat.id, message_id=to_pin)
        handlers_def.action(message)
    except Exception:
        bot.send_message(message.chat.id, 'Что-то пошло не так. Проблемы на нашей стороне.')
        handlers_def.action(message)

@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    if callback.data == 'review':
        bot.send_message(callback.message.chat.id,
                         'Оставь свой отзыв о боте, пожалуйста! Ваше мнение очень важно для нас)')
        bot.register_next_step_handler(callback.message, handlers_def.add_feedback)
    if callback.data == 'choose_time':
        bot.send_message(callback.message.chat.id, 'Напишите удобное время отправки напоминания в формате hh:mm')

        bot.register_next_step_handler(callback.message, handlers_def.change_time)

    if callback.data == 'change_info':
        try:
            connection = psycopg2.connect(dbname = config.db_name, user= config.db_user)
            cur = connection.cursor()
            cur.execute("SELECT name, id FROM memento.users where chat_id ='%s' " % (callback.message.chat.id))
            list_for_update = cur.fetchall()
            if list_for_update is not None:
                markup_change = types.InlineKeyboardMarkup()
                for list in list_for_update:
                    btn_change = types.InlineKeyboardButton(list[0], callback_data = "N_" + str(list[1]))
                    markup_change.add(btn_change)
                bot.send_message(callback.message.chat.id, 'Выберите запись для изменения:', reply_markup=markup_change)
            else:
                bot.send_message(callback.message.chat.id, 'У вас нет добавленных пользователей')
                handlers_def.action(callback.message)
            cur.close()
            connection.close()
        except Exception:
            bot.send_message(callback.message.chat.id, 'Что-то пошло не так')
            handlers_def.action(callback.message)
    if "N_" in callback.data:
        try:
            connection = psycopg2.connect(dbname = config.db_name, user= config.db_user)
            cur = connection.cursor()
            cur.execute("SELECT name, to_char(date_of_bd,'dd.mm.yyyy'), phone, email, information,id, 'for_delete' FROM memento.users where id = '%s' " % (callback.data[2:]))
            list_of_attributes = cur.fetchall()
            if list_of_attributes is not None:
                markup3 = types.InlineKeyboardMarkup()
                for list in list_of_attributes:
                    btn_change2 = types.InlineKeyboardButton('Имя: ' + list[0], callback_data="NP_" + 'name' + str(list[5]))
                    btn_change3 = types.InlineKeyboardButton('Дата рождения: ' + list[1], callback_data="NP_" + 'date_of_bd' + str(list[5]))
                    btn_change4 = types.InlineKeyboardButton('Телефон: ' + list[2], callback_data="NP_" + 'phone' + str(list[5]))
                    btn_change5 = types.InlineKeyboardButton('Почта: ' + list[3], callback_data="NP_" + 'email' + str(list[5]))
                    btn_change6 = types.InlineKeyboardButton('Информация: ' + list[4], callback_data="NP_" + 'information' + str(list[5]))
                    btn_del = types.InlineKeyboardButton('Удалить запись', callback_data= "NP_" + 'delete' + str(list[5]) + '~' + str(list[0]))
                    btn_main = types.InlineKeyboardButton('Вернуться в главное меню <<<', callback_data = "menu")
                    markup3.add(btn_change2).add(btn_change3).add(btn_change4).add(btn_change5).add(btn_change6).add(btn_del).add(btn_main)
                bot.send_message(callback.message.chat.id, 'Выберите запись для изменения:', reply_markup=markup3)
            else:
                bot.send_message(callback.message.chat.id, 'Что-то пошло не так')
                handlers_def.action(callback.message)
            cur.close()
            connection.close()
        except Exception:
            bot.send_message(callback.message.chat.id, 'Что-то пошло не так')
            handlers_def.action(callback.message)
    if "NP_" in callback.data and "delete" in callback.data:
        try:
            connection = psycopg2.connect(dbname=config.db_name, user=config.db_user)
            cur = connection.cursor()
            cur.execute("DELETE FROM memento.users WHERE id = '%s' " % (callback.data[9:].split('~',1)[0]))
            connection.commit()
            cur.close()
            connection.close()
            bot.send_message(callback.message.chat.id, 'Запись' + callback.data[9:].split('~',1)[1] + 'удалена!')
            handlers_def.action(callback.message)
        except Exception:
            bot.send_message(callback.message.chat.id, 'Что-то пошло не так')
            handlers_def.action(callback.message)
    if callback.data == "menu":
        handlers_def.action(callback.message)
    if "NP_" in callback.data and "name" in callback.data:
        bot.send_message(callback.message.chat.id, 'Введите новое значение')

        def change_name(message):
            try:
                connection = psycopg2.connect(dbname = config.db_name, user= config.db_user)
                cur = connection.cursor()
                cur.execute(
                    "UPDATE memento.users SET update_dt = current_timestamp, name = '%s' where id = '%s' " % (
                    message.text.strip(), callback.data[7:]))
                bot.send_message(callback.message.chat.id, 'Имя пользователя изменено успешно!')
                connection.commit()
                cur.close()
                connection.close()
                handlers_def.action(message)
            except Exception:
                bot.send_message(callback.message.chat.id, 'Не удалость подключиться к базе(')
                handlers_def.action(message)
            #TODO: прописать возвращение к выбору записей для изменения
        bot.register_next_step_handler(callback.message, change_name)
    if "NP_" in callback.data and "date_of_bd" in callback.data:
        bot.send_message(callback.message.chat.id, 'Введите новое значение')
        def change_date_of_bd(message):
            pattern = re.compile(r'^([0-9]{2}\.[0-9]{2}\.[0-9]{4})$')

            if pattern.match(message.text.strip()):
                try:
                    dateparts = callback.message.text.strip().split('.')
                    dateobj = datetime.date(int(dateparts[2]), int(dateparts[1]), int(dateparts[0]))
                    connection = psycopg2.connect(dbname = config.db_name, user= config.db_user)
                    cur = connection.cursor()
                    cur.execute(
                        "UPDATE memento.users SET update_dt = current_timestamp, to_char(date_of_bd,'dd.mm.yyyy') = '%s' where id = '%s' " % (
                        message.text.strip(), callback.data[13:]))
                    bot.send_message(callback.message.chat.id, 'Дата рождения пользователя изменена успешно!')
                    connection.commit()
                    cur.close()
                    connection.close()
                    handlers_def.action(message)
                except Exception:
                    bot.send_message(callback.message.chat.id, 'Неправильный формат ввода')
                    handlers_def.action(message)

        bot.register_next_step_handler(callback.message, change_date_of_bd)

    if "NP_" in callback.data and "phone" in callback.data:
        bot.send_message(callback.message.chat.id, 'Введите новое значение')
        def change_phone(message):
            try:
                connection = psycopg2.connect(dbname = config.db_name, user= config.db_user)
                cur = connection.cursor()
                cur.execute(
                    "UPDATE memento.users SET update_dt = current_timestamp, phone = '%s' where id = '%s' " % (message.text.strip(), callback.data[8:]))
                bot.send_message(callback.message.chat.id, 'Телефон пользователя изменен успешно!')
                connection.commit()
                cur.close()
                connection.close()
                handlers_def.action(callback.message)
            except Exception:
                bot.send_message(callback.message.chat.id, 'Не удалость подключиться к базе(')
                handlers_def.action(message)

        bot.register_next_step_handler(callback.message, change_phone)
    if "NP_" in callback.data and "email" in callback.data:
        bot.send_message(callback.message.chat.id, 'Введите новое значение')

        def change_email(message):
            try:
                connection = psycopg2.connect(dbname = config.db_name, user= config.db_user)
                cur = connection.cursor()
                cur.execute(
                    "UPDATE memento.users SET update_dt = current_timestamp, email = '%s' where id = '%s' " % (message.text.strip(), callback.data[8:]))
                bot.send_message(callback.message.chat.id, 'Почта пользователя изменена успешно!')
                connection.commit()
                cur.close()
                connection.close()
                handlers_def.action(callback.message)
            except Exception:
                bot.send_message(callback.message.chat.id, 'Не удалость подключиться к базе(')
                handlers_def.action(message)

        bot.register_next_step_handler(callback.message, change_email)
    if "NP_" in callback.data and "information" in callback.data:
        bot.send_message(callback.message.chat.id, 'Введите новое значение')
        def change_information(message):
            try:
                connection = psycopg2.connect(dbname = config.db_name, user= config.db_user)
                cur = connection.cursor()
                cur.execute(
                    "UPDATE memento.users SET update_dt = current_timestamp, information = '%s' where id = '%s' " % (message.text.strip(), callback.data[14:]))
                bot.send_message(callback.message.chat.id, 'Информация о пользователу изменена успешно!')
                connection.commit()
                cur.close()
                connection.close()
                handlers_def.action(callback.message)
            except Exception:
                bot.send_message(callback.message.chat.id, 'Не удалость подключиться к базе(')
                handlers_def.action(message)


        bot.register_next_step_handler(callback.message, change_information)
    if callback.data == 'add bd':
        global list_of_inserts
        list_of_inserts[callback.message.chat.id] = ['','','','','']
        #атрибуты: chat.id, date_of_bd, name, phone, email, information
        markup1 = types.ReplyKeyboardMarkup(resize_keyboard=True)
        bot.send_message(callback.message.chat.id, 'Введите дату в формате дд.мм.гггг', reply_markup=markup1)
        def handle_bd(message):
                pattern = re.compile(r'^([0-9]{2}\.[0-9]{2}\.[0-9]{4})$')
                if pattern.match(message.text.strip()):
                    list_of_inserts[message.chat.id][0] = message.text.strip()
                    try:
                        dateparts = message.text.strip().split('.')
                        dateobj = datetime.date(int(dateparts[2]),int(dateparts[1]),int(dateparts[0]))
                        msg = bot.reply_to(message, 'Введите имя и фамилию', reply_markup=markup1)
                        bot.register_next_step_handler(msg, process_name)
                    except Exception:
                        bot.send_message(message.chat.id, 'Неправильный формат ввода')
                        handlers_def.action(message)
                else:
                    bot.send_message(message.chat.id, 'Неправильный формат ввода')
                    handlers_def.action(message)

        bot.register_next_step_handler(callback.message, handle_bd)
        def process_name(message):
            list_of_inserts[message.chat.id][1] = message.text.strip()
            btn_skip2 = types.KeyboardButton('Пропустить ввод телефона')
            markup2 = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup2.add(btn_skip2)
            msg = bot.reply_to(message, 'Введите номер телефона', reply_markup=markup2)
            bot.register_next_step_handler(msg, process_phone)
        def process_phone(message):
            if (message.text == 'Пропустить ввод телефона'):
                list_of_inserts[message.chat.id][2] = ''
            else:
                list_of_inserts[message.chat.id][2] = message.text.strip()
            btn_skip3 = types.KeyboardButton('Пропустить ввод почты')
            markup7 = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup7.add(btn_skip3)
            msg = bot.reply_to(message, 'Введите почту', reply_markup=markup7)
            bot.register_next_step_handler(msg, process_email)
        def process_email(message):
            if (message.text ==  'Пропустить ввод почты'):
                list_of_inserts[message.chat.id][3] = ''
            else:
                list_of_inserts[message.chat.id][3] = message.text.strip()
            markup4 = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn_skip4 = types.KeyboardButton('Пропустить ввод информации')
            markup4.add(btn_skip4)
            msg = bot.reply_to(message, 'Введите краткую информацию о человеке', reply_markup=markup4)
            bot.register_next_step_handler(msg, process_information)

        def process_information(message):
            if (message.text == 'Пропустить ввод информации'):
                list_of_inserts[message.chat.id][4] = ''
            else:
                list_of_inserts[message.chat.id][4] = message.text.strip()
            add_record_into_db(message)

        def add_record_into_db(message):
            try:
                connection = psycopg2.connect(dbname = config.db_name, user= config.db_user)
                cur = connection.cursor()
                cur.execute(
                    "INSERT INTO memento.users(name, date_of_bd, chat_id, phone, email, information) VALUES ('%s', to_date('%s','dd.mm.yyyy'), '%s', '%s', '%s', '%s')" % (
                    list_of_inserts[message.chat.id][1], list_of_inserts[message.chat.id][0], message.chat.id, list_of_inserts[message.chat.id][2], list_of_inserts[message.chat.id][3], list_of_inserts[message.chat.id][4]))
                bot.reply_to(message, 'Добавлен пользователь: ' + list_of_inserts[message.chat.id][1], reply_markup=types.ReplyKeyboardRemove())
                list_of_inserts[message.chat.id] = ['','','','','']
                connection.commit()
                cur.close()
                connection.close()
                handlers_def.action(message)
            except Exception:
                bot.send_message(message.chat.id, 'Что-то пошло не так. Скорее всего, что-то не так с вводимыми данными.')
                handlers_def.action(message)



    if callback.data == 'show bd':
        try:
            connection = psycopg2.connect(dbname = config.db_name, user= config.db_user)
            cur = connection.cursor()
            cur.execute("SELECT name, to_char(date_of_bd,'dd.mm.yyyy') FROM memento.users where chat_id ='%s' order by name " % (callback.message.chat.id))
            users = cur.fetchall()
            s = ''
            if len(users) != 0:
                for user in users:
                    s = s + user[1] + ' ' + ':' + ' '
                    s = s + user[0] + '\n'
                bot.send_message(callback.message.chat.id, s)
            else:
                bot.send_message(callback.message.chat.id, 'Список пуст!')
            cur.close()
            connection.close()
            handlers_def.action(callback.message)
        except Exception:
            bot.send_message(callback.message.chat.id, 'Что-то пошло не так :(')
            handlers_def.action(callback.message)

if __name__ == "__main__":
    schedule.every().minute.do(function_to_run)
    Thread(target=schedule_checker).start()

bot.infinity_polling()

