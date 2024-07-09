# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import schedule
import re
import time
import datetime
from threading import Thread
from time import sleep
import telebot
from telebot import types
def schedule_checker():
    while True:
        schedule.run_pending()
        sleep(1)
def function_to_run():
    try:
        connection = psycopg2.connect(dbname='polluvna', user='polluvna', password='KyFPza0pFLM7', host='158.160.137.15')
        curs = connection.cursor()
        curs.execute(" SELECT u.name, st.chat_id FROM public.send_time st JOIN public.users u ON u.chat_id = st.chat_id where extract(day from u.date_of_bd) = extract(day from current_timestamp) and extract(month from u.date_of_bd) = extract(month from current_timestamp) and extract(hour from to_timestamp(st.time,'HH24:MI')) = extract(hour from current_timestamp) and extract(minute from to_timestamp(st.time,'HH24:MI')) = extract(minute from current_timestamp) ")
        users1 = curs.fetchall()
        for user in users1:
            bot.send_message(user[1], 'Не забудьте поздравить этого человека с др:' + user[0])
        curs.close()
        connection.close()
    except Exception:
        bot.send_message(user[1], 'Что-то пошло не так при попытке похода в базу. ')

bot = telebot.TeleBot('6827864691:AAH2MPjAwSdaQctyiic5Z2Nbo30AQ8rxMl8')
date_of_bd = None
chat_id_tg = None
name = None
phone = None
email = None
information = None
message_chat_id = None
list_for_update = []
list_of_inserts = [] #словарь для вставок пользователей. 1 пользователь = 1 запись
import psycopg2
try:
    connection = psycopg2.connect(dbname='polluvna', user='polluvna', password='KyFPza0pFLM7', host='158.160.137.15')
    cur = connection.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS public.users(name varchar(100), date_of_bd date, chat_id varchar(100), phone varchar(100), email varchar(100), information varchar(200))')
    cur.execute('CREATE TABLE IF NOT EXISTS public.send_time(name varchar (100), time varchar(50), chat_id varchar(100))')
    connection.commit()
    cur.close()
    connection.close()
except Exception:
    print('Не удалось подключиться к базе')
@bot.message_handler(commands=['start','hello'])
def start(message):
    #TODO: сделать приветственное сообщение (функционал бота, пожертвования и тд)
    try:
        connection = psycopg2.connect(dbname='polluvna', user='polluvna', password='KyFPza0pFLM7', host='158.160.137.15')
        cur = connection.cursor()
        cur.execute("SELECT chat_id FROM public.send_time")
        send_time_chat_ids = cur.fetchall()
        chat_id_array = []
        for chat_ids in send_time_chat_ids:
            chat_id_array.append(chat_ids[0])
        if str(message.chat.id) not in chat_id_array:
            cur.execute(
                "INSERT INTO public.send_time(time, chat_id) VALUES ('%s', '%s')" % ('9:00', message.chat.id))
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
        action(message)
    except Exception:
        bot.send_message(message.chat.id, 'Что-то пошло не так. Проблемы на нашей стороне.')
        action(message)


@bot.message_handler(commands=['action'])
def action(message: types.Message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("Внесите ДР", callback_data='add bd')
    btn2 = types.InlineKeyboardButton("Показать список ДР", callback_data='show bd')
    btn3 = types.InlineKeyboardButton("Изменить запись", callback_data='change_info')
    btntime = types.InlineKeyboardButton("Время отправки", callback_data='choose_time')
    markup.add(btn1).add(btn2).add(btn3).add(btntime)
    global user_id_tg
    bot.send_message(message.chat.id, 'Выберите действие:', reply_markup=markup)

@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    if callback.data == 'choose_time':
        bot.send_message(callback.message.chat.id, 'Напишите удобное время отправки напоминания в формате hh:mm')

        @bot.message_handler(content_types=['text'])
        def change_time(message):
            #TODO: проверить формат времени (:)
            try:
                time.strptime(message.text.strip(), '%H:%M')
                connection = psycopg2.connect(dbname='polluvna', user='polluvna', password='KyFPza0pFLM7',
                                              host='158.160.137.15')
                cur = connection.cursor()
                cur.execute("UPDATE public.send_time SET time = '%s'  WHERE chat_id ='%s' " % (
                message.text.strip(), message.chat.id))
                connection.commit()
                cur.close()
                connection.close()
                bot.send_message(message.chat.id, 'Время изменено успешно')
                action(message)
            except ValueError:
                bot.send_message(message.chat.id, 'Что-то пошло не так. Попробуйте другие данные.')
                action(message)
    if callback.data == 'change_info':
            connection = psycopg2.connect(dbname='polluvna', user='polluvna', password='KyFPza0pFLM7',
                                          host='158.160.137.15')
            cur = connection.cursor()
            cur.execute("SELECT name, id FROM public.users where chat_id ='%s' " % (callback.message.chat.id))
            list_for_update = cur.fetchall()
            if list_for_update is not None:
                markup_change = types.InlineKeyboardMarkup()
                for list in list_for_update:
                    btn_change = types.InlineKeyboardButton(list[0], callback_data = "N_" + str(list[1]))
                    markup_change.add(btn_change)
                bot.send_message(callback.message.chat.id, 'Выберите запись для изменения:', reply_markup=markup_change)
            else:
                bot.send_message(callback.message.chat.id, 'У вас нет добавленных пользователей')
                action(callback.message)
            cur.close()
            connection.close()
    #TODO: подумать как выводить пользователя из режима изменения записей. наверное, главное меню (кнопка)

    if "N_" in callback.data:
        connection = psycopg2.connect(dbname='polluvna', user='polluvna', password='KyFPza0pFLM7',
                                      host='158.160.137.15')
        cur = connection.cursor()
        cur.execute("SELECT name, to_char(date_of_bd,'dd.mm.yyyy'), phone, email, information,id FROM public.users where id = '%s' " % (callback.data[2:]))
        list_of_attributes = cur.fetchall()
        if list_of_attributes is not None:
            markup3 = types.InlineKeyboardMarkup()
            for list in list_of_attributes:
                btn_change2 = types.InlineKeyboardButton('Имя: ' + list[0], callback_data="NP_" + 'name' + str(list[5]))
                btn_change3 = types.InlineKeyboardButton('Дата рождения: ' + list[1], callback_data="NP_" + 'date_of_bd' + str(list[5]))
                btn_change4 = types.InlineKeyboardButton('Телефон: ' + list[2], callback_data="NP_" + 'phone' + str(list[5]))
                btn_change5 = types.InlineKeyboardButton('Почта: ' + list[3], callback_data="NP_" + 'email' + str(list[5]))
                btn_change6 = types.InlineKeyboardButton('Информация: ' + list[4], callback_data="NP_" + 'information' + str(list[5]))
                btn_main = types.InlineKeyboardButton('Вернуться в главное меню <<<', callback_data = "menu")
                markup3.add(btn_change2).add(btn_change3).add(btn_change4).add(btn_change5).add(btn_change6).add(btn_main)
            bot.send_message(callback.message.chat.id, 'Выберите запись для изменения:', reply_markup=markup3)
        else:
            bot.send_message(callback.message.chat.id, 'Что-то пошло не так')
            action(callback.message)
        cur.close()
        connection.close()
    if callback.data == "menu":
        action(callback.message)
    if "NP_" in callback.data and "name" in callback.data:
        bot.send_message(callback.message.chat.id, 'Введите новое значение')

        @bot.message_handler(content_types=['text'])
        def change_name(message):
            connection = psycopg2.connect(dbname='polluvna', user='polluvna', password='KyFPza0pFLM7',
                                          host='158.160.137.15')
            cur = connection.cursor()
            cur.execute(
                "UPDATE public.users SET name = '%s' where id = '%s' " % (message.text.strip(), callback.data[7:]))
            bot.send_message(callback.message.chat.id, 'Имя пользователя изменено успешно!')
            connection.commit()
            cur.close()
            connection.close()
            markup_main2 = types.InlineKeyboardMarkup()
            btn_main = types.InlineKeyboardButton("Вернуться в главное меню", callback_data='main')
            btn_change_other = types.InlineKeyboardButton("Вернуться к записям для изменений", callback_data='back')
            markup_main2.add(btn_main).add(btn_change_other)
            bot.send_message(callback.message.chat.id, 'Выберите действие:', reply_markup=markup_main2)
            if callback.data == "main":
                action(message)
            #TODO: прописать возвращение к выбору записей для изменения
    if "NP_" in callback.data and "date_of_bd" in callback.data:
        bot.send_message(callback.message.chat.id, 'Введите новое значение')
        @bot.message_handler(content_types=['text'])
        def change_date_of_bd(message):
            pattern = re.compile(r'^([0-9]{2}\.[0-9]{2}\.[0-9]{4})$')

            if pattern.match(message.text.strip()):
                try:
                    dateparts = callback.message.text.strip().split('.')
                    dateobj = datetime.date(int(dateparts[2]), int(dateparts[1]), int(dateparts[0]))
                    connection = psycopg2.connect(dbname='polluvna', user='polluvna', password='KyFPza0pFLM7',
                                                  host='158.160.137.15')
                    cur = connection.cursor()
                    cur.execute(
                        "UPDATE public.users SET to_char(date_of_bd,'dd.mm.yyyy') = '%s' where id = '%s' " % (
                        message.text.strip(), callback.data[13:]))
                    bot.send_message(callback.message.chat.id, 'Дата рождения пользователя изменена успешно!')
                    connection.commit()
                    cur.close()
                    connection.close()
                    action(message)
                except Exception:
                    bot.send_message(callback.message.chat.id, 'Неправильный формат ввода')
                    action(message)

    if "NP_" in callback.data and "phone" in callback.data:
        bot.send_message(callback.message.chat.id, 'Введите новое значение')

        @bot.message_handler(content_types=['text'])
        def change_phone(message):
            connection = psycopg2.connect(dbname='polluvna', user='polluvna', password='KyFPza0pFLM7',
                                          host='158.160.137.15')
            cur = connection.cursor()
            cur.execute(
                "UPDATE public.users SET phone = '%s' where id = '%s' " % (message.text.strip(), callback.data[8:]))
            bot.send_message(callback.message.chat.id, 'Телефон пользователя изменен успешно!')
            connection.commit()
            cur.close()
            connection.close()
            action(callback.message)
    if "NP_" in callback.data and "email" in callback.data:
        bot.send_message(callback.message.chat.id, 'Введите новое значение')

        @bot.message_handler(content_types=['text'])
        def change_email(message):
            connection = psycopg2.connect(dbname='polluvna', user='polluvna', password='KyFPza0pFLM7',
                                          host='158.160.137.15')
            cur = connection.cursor()
            cur.execute(
                "UPDATE public.users SET email = '%s' where id = '%s' " % (message.text.strip(), callback.data[8:]))
            bot.send_message(callback.message.chat.id, 'Почта пользователя изменена успешно!')
            connection.commit()
            cur.close()
            connection.close()
            action(callback.message)
    if "NP_" in callback.data and "information" in callback.data:
        bot.send_message(callback.message.chat.id, 'Введите новое значение')

        @bot.message_handler(content_types=['text'])
        def change_information(message):
            connection = psycopg2.connect(dbname='polluvna', user='polluvna', password='KyFPza0pFLM7',
                                          host='158.160.137.15')
            cur = connection.cursor()
            cur.execute(
                "UPDATE public.users SET information = '%s' where id = '%s' " % (message.text.strip(), callback.data[14:]))
            bot.send_message(callback.message.chat.id, 'Информация о пользователу изменена успешно!')
            connection.commit()
            cur.close()
            connection.close()
            action(callback.message)
    if callback.data == 'add bd':
        global list_of_inserts
        for len_list in range(len(list_of_inserts)):
            if list_of_inserts[len_list][0] == callback.message.chat.id:
                list_of_inserts.pop(len_list)
        list_of_inserts.append([callback.message.chat.id, '', '', '', '', ''])
        #атрибуты: chat.id, date_of_bd, name, phone, email, information
        markup1 = types.ReplyKeyboardMarkup(resize_keyboard=True)
        bot.send_message(callback.message.chat.id, 'Введите дату в формате дд.мм.гггг', reply_markup=markup1)
        @bot.message_handler(content_types=['text'])
        def handle_bd(message):
                #print(0)
                pattern = re.compile(r'^([0-9]{2}\.[0-9]{2}\.[0-9]{4})$')
                #print(1)
                if pattern.match(message.text.strip()):
                    #print(2)
                    for len_list in range (len(list_of_inserts)):
                        if list_of_inserts[len_list][0] == message.chat.id:
                            list_of_inserts[len_list][1] = message.text.strip()
                    try:
                        dateparts = message.text.strip().split('.')
                        dateobj = datetime.date(int(dateparts[2]),int(dateparts[1]),int(dateparts[0]))
                        msg = bot.reply_to(message, 'Введите имя и фамилию', reply_markup=markup1)
                        bot.register_next_step_handler(msg, process_name)
                    except Exception:
                        bot.send_message(message.chat.id, 'Неправильный формат ввода')
                        action(message)
                else:
                    #print(3)
                    bot.send_message(message.chat.id, 'Неправильный формат ввода')
                    action(message)
        def process_name(message):
            for len_list in range(len(list_of_inserts)):
                if list_of_inserts[len_list][0] == message.chat.id:
                    list_of_inserts[len_list][2] = message.text.strip()
            btn_skip2 = types.KeyboardButton('Пропустить ввод телефона')
            markup2 = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup2.add(btn_skip2)
            msg = bot.reply_to(message, 'Введите номер телефона', reply_markup=markup2)
            bot.register_next_step_handler(msg, process_phone)
        def process_phone(message):
            if (message.text == 'Пропустить ввод телефона'):
                for len_list in range(len(list_of_inserts)):
                    if list_of_inserts[len_list][0] == message.chat.id:
                        list_of_inserts[len_list][3] = ''
                        #process_email(message)
            else:
                for len_list in range(len(list_of_inserts)):
                    if list_of_inserts[len_list][0] == message.chat.id:
                        list_of_inserts[len_list][3] = message.text.strip()
            btn_skip3 = types.KeyboardButton('Пропустить ввод почты')
            markup7 = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup7.add(btn_skip3)
            msg = bot.reply_to(message, 'Введите почту', reply_markup=markup7)
            bot.register_next_step_handler(msg, process_email)
        def process_email(message):
            if (message.text ==  'Пропустить ввод почты'):
                for len_list in range(len(list_of_inserts)):
                    if list_of_inserts[len_list][0] == message.chat.id:
                        list_of_inserts[len_list][4] = ''
                        #process_information(message)
            else:
                for len_list in range(len(list_of_inserts)):
                    if list_of_inserts[len_list][0] == message.chat.id:
                        list_of_inserts[len_list][4] = message.text.strip()
            markup4 = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn_skip4 = types.KeyboardButton('Пропустить ввод информации')
            markup4.add(btn_skip4)
            msg = bot.reply_to(message, 'Введите краткую информацию о человеке', reply_markup=markup4)
            bot.register_next_step_handler(msg, process_information)

        def process_information(message):
            if (message.text == 'Пропустить ввод информации'):
                for len_list in range(len(list_of_inserts)):
                    if list_of_inserts[len_list][0] == message.chat.id:
                        list_of_inserts[len_list][5] = ''
            else:
                for len_list in range(len(list_of_inserts)):
                    if list_of_inserts[len_list][0] == message.chat.id:
                        list_of_inserts[len_list][5] = message.text.strip()
            add_record_into_db(message)

        def add_record_into_db(message):
            try:
                connection = psycopg2.connect(dbname='polluvna', user='polluvna', password='KyFPza0pFLM7',
                                              host='158.160.137.15')
                print(datetime.datetime.now(), message.chat.id, 'connect')
                cur = connection.cursor()
                print(datetime.datetime.now(), message.chat.id, 'cursor')
                for len_list in range(len(list_of_inserts)):
                    print(datetime.datetime.now(), message.chat.id, 'for', list_of_inserts)
                    if list_of_inserts[len_list][0] == message.chat.id:
                        print(datetime.datetime.now(), message.chat.id, 'if')
                        cur.execute(
                            "INSERT INTO public.users(name, date_of_bd, chat_id, phone, email, information) VALUES ('%s', to_date('%s','dd.mm.yyyy'), '%s', '%s', '%s', '%s')" % (
                        list_of_inserts[len_list][2], list_of_inserts[len_list][1], list_of_inserts[len_list][0], list_of_inserts[len_list][3], list_of_inserts[len_list][4], list_of_inserts[len_list][5]))
                        bot.reply_to(message, 'Добавлен пользователь: ' + list_of_inserts[len_list][2], reply_markup=types.ReplyKeyboardRemove())
                        print(datetime.datetime.now(), message.chat.id, 'insert')
                        list_of_inserts.pop(len_list)
                        print(datetime.datetime.now(), message.chat.id, 'pop')
                print(datetime.datetime.now(), message.chat.id, 'добавлен пользователь')

                connection.commit()
                print(datetime.datetime.now(), message.chat.id, 'commit')
                cur.close()
                print(datetime.datetime.now(), message.chat.id, 'cur.close')
                connection.close()
                print(datetime.datetime.now(), message.chat.id, 'conn.close')
                action(message)
            except Exception:
                bot.send_message(message.chat.id, 'Что-то пошло не так. Скорее всего, что-то не так с вводимыми данными.')
                action(message)



    if callback.data == 'show bd':
        try:
            connection = psycopg2.connect(dbname='polluvna', user='polluvna', password='KyFPza0pFLM7', host='158.160.137.15')
            cur = connection.cursor()
            cur.execute("SELECT name, to_char(date_of_bd,'dd.mm.yyyy') FROM public.users where chat_id ='%s' order by name " % (callback.message.chat.id))
            users = cur.fetchall()
            s = ''
            if len(users) != 0:
                for user in users:
                    for name in user:
                        s = s + ' ' + name + '\n'
                bot.send_message(callback.message.chat.id, s)
            else:
                bot.send_message(callback.message.chat.id, 'Список пуст!')
            cur.close()
            connection.close()
            action(callback.message)
        except Exception:
            bot.send_message(callback.message.chat.id, 'Что-то пошло не так :(')
            action(callback.message)

if __name__ == "__main__":
    schedule.every().minute.do(function_to_run)
    Thread(target=schedule_checker).start()

bot.infinity_polling()

