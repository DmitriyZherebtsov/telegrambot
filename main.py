# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import schedule
import re
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
        bot.send_message(message.chat.id,'Здравствуйте, повелитель!')
        action(message)
    except Exception:
        bot.send_message(message.chat.id, 'Что-то пошло не так. Проблемы на нашей стороне.')
        action(message)


@bot.message_handler(commands=['action'])
def action(message: types.Message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("Внесите ДР", callback_data='add bd')
    btn2 = types.InlineKeyboardButton("Показать список ДР", callback_data='show bd')
    btn3 = types.InlineKeyboardButton("Изменить пользователя", callback_data='change_info')
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
                connection = psycopg2.connect(dbname='polluvna', user='polluvna', password='KyFPza0pFLM7', host='158.160.137.15')
                cur = connection.cursor()
                cur.execute("UPDATE public.send_time SET time = '%s'  WHERE chat_id ='%s' " % (message.text.strip(), message.chat.id))
                connection.commit()
                cur.close()
                connection.close()
                bot.send_message(message.chat.id, 'Время изменено успешно')
                action(message)
            except Exception:
                bot.send_message(message.chat.id, 'Что-то пошло не так. Попробуйте другие данные.')
                action(message)
    if callback.data == 'change_info':
        try:
            connection = psycopg2.connect(dbname='polluvna', user='polluvna', password='KyFPza0pFLM7', host='158.160.137.15')
            cur = connection.cursor()
            cur.execute("SELECT name FROM public.users where chat_id ='%s' " % (callback.message.chat.id))
            users = cur.fetchall()
            for user in users:
                x = ' '
                for name in user:
                    x = name
                    markup = types.InlineKeyboardMarkup()
                    btn_change = types.InlineKeyboardButton(x, callback_data='change_info')
                    markup.add(btn_change)
                    bot.send_message(callback.message.chat.id, reply_markup=markup)
            cur.close()
            connection.close()
            action(callback.message)
            cur.execute("SELECT name FROM public.users where chat_id ='%s' " % (callback.message.chat.id))
            ''' '#вывод кнопок после выбранного юзера
            markup = types.InlineKeyboardMarkup()
            btn4 = types.InlineKeyboardButton("Имя и фамилия", callback_data='name_surname')
            btn5 = types.InlineKeyboardButton("Дата рождения", callback_data='date_bd')
            btn6 = types.InlineKeyboardButton("Номер телефона", callback_data='phone')
            btn7 = types.InlineKeyboardButton("Почта", callback_data='email')
            btn8 = types.InlineKeyboardButton("Информация", callback_data='info')
            markup.add(btn4, btn5, btn6, btn7, btn8)
            bot.send_message(callback.message.chat.id, 'Что вы хотите изменить?', reply_markup=markup)
            '''
        except Exception:
            bot.send_message(callback.message.chat.id, 'Что-то пошло не так :(')
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
                pattern = re.compile(r'^([0-9]{2}\.[0-9]{2}\.[0-9]{4})$')

                if pattern.match(message.text.strip()):
                    #date_of_bd = message.text.strip()
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
                    bot.send_message(message.chat.id, 'Неправильный формат ввода')
                    action(message)
        def process_name(message):
                for len_list in range(len(list_of_inserts)):
                    if list_of_inserts[len_list][0] == message.chat.id:
                        list_of_inserts[len_list][2] = message.text.strip()

                msg = bot.reply_to(message, 'Введите номер телефона', reply_markup=markup1)
                bot.register_next_step_handler(msg, process_phone)
        def process_phone(message):
            markup2 = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn_skip2 = types.KeyboardButton('Пропустить ввод телефона')
            markup2.add(btn_skip2)
            if (message.text == 'Пропустить ввод телефона'):
                global phone
                phone = ''
                process_email(message)
            else:
                for len_list in range(len(list_of_inserts)):
                    if list_of_inserts[len_list][0] == message.chat.id:
                        list_of_inserts[len_list][3] = message.text.strip()

                msg = bot.reply_to(message, 'Введите почту')
                bot.register_next_step_handler(msg, process_email)
        def process_email(message):
            markup3 = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn_skip3 = types.KeyboardButton('Пропустить ввод почты')
            markup3.add(btn_skip3)
            if (message.text ==  'Пропустить ввод почты'):
                global email
                email = ''
                process_information(message)
            else:
                for len_list in range(len(list_of_inserts)):
                    if list_of_inserts[len_list][0] == message.chat.id:
                        list_of_inserts[len_list][4] = message.text.strip()

                msg = bot.reply_to(message, 'Введите краткую информацию о человеке')
                bot.register_next_step_handler(msg, process_information)

        def process_information(message):
            markup4 = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn_skip4 = types.KeyboardButton('Пропустить ввод информации')
            markup4.add(btn_skip4)
            if (message.text == 'Пропустить ввод информации'):
                global information
                information = ''
            else:
                for len_list in range(len(list_of_inserts)):
                    if list_of_inserts[len_list][0] == message.chat.id:
                        list_of_inserts[len_list][5] = message.text.strip()

            try:
                connection = psycopg2.connect(dbname='polluvna', user='polluvna', password='KyFPza0pFLM7',
                                              host='158.160.137.15')
                cur = connection.cursor()
                for len_list in range(len(list_of_inserts)):
                    if list_of_inserts[len_list][0] == message.chat.id:
                        cur.execute(
                            "INSERT INTO public.users(name, date_of_bd, chat_id, phone, email, information) VALUES ('%s', to_date('%s','dd.mm.yyyy'), '%s', '%s', '%s', '%s')" % (
                        list_of_inserts[len_list][2], list_of_inserts[len_list][1], list_of_inserts[len_list][0], list_of_inserts[len_list][3], list_of_inserts[len_list][4], list_of_inserts[len_list][5]))
                        bot.reply_to(message, 'Добавлен пользователь: ' + list_of_inserts[len_list][2])
                        list_of_inserts.pop(len_list)

                connection.commit()
                cur.close()
                connection.close()
                action(message)
            except Exception:
                bot.send_message(message.chat.id, 'Что-то пошло не так. Скорее всего, что-то не так с вводимыми данными.')
                action(message)



    if callback.data == 'show bd':
        try:
            connection = psycopg2.connect(dbname='polluvna', user='polluvna', password='KyFPza0pFLM7', host='158.160.137.15')
            cur = connection.cursor()
            cur.execute("SELECT name, to_char(date_of_bd,'dd.mm.yyyy') FROM public.users where chat_id ='%s' " % (callback.message.chat.id))
            users = cur.fetchall()
            if len(users) != 0:
                for user in users:
                    s = ' '
                    for name in user:
                        s = s + ' ' + name
                        s = s + '\n'
                    if s != ' ':
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

