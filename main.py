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
bot = telebot.TeleBot('6827864691:AAH2MPjAwSdaQctyiic5Z2Nbo30AQ8rxMl8')
date_of_bd = None
chat_id_tg = None
name = None
phone = None
email = None
information = None
message_chat_id = None
time = '9:00'
import psycopg2
connection = psycopg2.connect(dbname='polluvna', user='polluvna', password='KyFPza0pFLM7', host='158.160.137.15')
cur = connection.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS public.users(name varchar(100), date_of_bd date, chat_id varchar(100), phone varchar(100), email varchar(100), information varchar(200))')
#cur.execute('drop table public.send_time')
cur.execute('CREATE TABLE IF NOT EXISTS public.send_time(name varchar (100), time varchar(50), chat_id varchar(100))')
connection.commit()
cur.close()
connection.close()
@bot.message_handler(commands=['start','hello'])
def start(message):
    connection = psycopg2.connect(dbname='polluvna', user='polluvna', password='KyFPza0pFLM7', host='158.160.137.15')
    cur = connection.cursor()
    cur.execute("SELECT chat_id FROM public.send_time")
    send_time_chat_ids = cur.fetchall()
    chat_id_array = []
    for chat_ids in send_time_chat_ids:
        chat_id_array.append(chat_ids[0])
    if str(message.chat.id) not in chat_id_array:
        cur.execute(
            "INSERT INTO public.send_time(time, chat_id) VALUES ('%s', '%s')" % (time, message.chat.id))
    connection.commit()
    cur.close()
    connection.close()
    bot.send_message(message.chat.id,'Здравствуйте, повелитель!')
    action(message)
def schedule_checker():
    while True:
        schedule.run_pending()
        sleep(1)
def function_to_run():
    connection = psycopg2.connect(dbname='polluvna', user='polluvna', password='KyFPza0pFLM7', host='158.160.137.15')
    curs = connection.cursor()
    curs.execute(" SELECT u.name, st.chat_id FROM public.send_time st JOIN public.users u ON u.chat_id = st.chat_id where extract(day from u.date_of_bd) = extract(day from current_timestamp) and extract(month from u.date_of_bd) = extract(month from current_timestamp) and extract(hour from to_timestamp(st.time,'HH24:MI')) = extract(hour from current_timestamp) and extract(minute from to_timestamp(st.time,'HH24:MI')) = extract(minute from current_timestamp) ")
    users1 = curs.fetchall()
    for user in users1:
        bot.send_message(user[1], 'Не забудьте поздравить этого человека с др:' + user[0])
    curs.close()
    connection.close()
if __name__ == "__main__":
    schedule.every().minute.do(function_to_run)
    Thread(target=schedule_checker).start()
@bot.message_handler(commands=['action'])
def action(message: types.Message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("Внесите ДР", callback_data='add bd')
    btn2 = types.InlineKeyboardButton("Показать список ДР", callback_data='show bd')
    btn3 = types.InlineKeyboardButton("Изменить пользователя", callback_data='change_info')
    btntime = types.InlineKeyboardButton("Время отправки", callback_data='choose_time')
    markup.add(btn1, btn2, btn3,btntime)
    global user_id_tg
    bot.send_message(message.chat.id, 'Выберите действие:', reply_markup=markup)

@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    if callback.data == 'choose_time':
        bot.send_message(callback.message.chat.id, 'Напишите удобное время отправки напоминания в формате hh:mm')

        @bot.message_handler(content_types=['text'])
        def change_time(message):
            global time
            global message_chat_id
            time = message.text.strip()
            connection = psycopg2.connect(dbname='polluvna', user='polluvna', password='KyFPza0pFLM7', host='158.160.137.15')
            cur = connection.cursor()
            cur.execute("UPDATE public.send_time SET time = '%s'  WHERE chat_id ='%s' " % (time, message.chat.id))
            connection.commit()
            cur.close()
            connection.close()
            action(message)
    if callback.data == 'change_info':
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
        action(message_chat_id)
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
    if callback.data == 'add bd':
        #def insert_user(message: types.Message):
        markup1 = types.ReplyKeyboardMarkup(resize_keyboard=True)
        bot.send_message(callback.message.chat.id, 'Введите дату в формате дд.мм.гггг', reply_markup=markup1)
        @bot.message_handler(content_types=['text'])
        def handle_bd(message):
                global date_of_bd
                pattern = re.compile(r'^([0-9]{2}\.[0-9]{2}\.[0-9]{4})$')
                date_of_bd = message.text.strip()
                if pattern.match(message.text.strip()):
                    msg = bot.reply_to(message, 'Введите имя и фамилию', reply_markup=markup1)
                    bot.register_next_step_handler(msg, process_name)
                else:
                    bot.send_message(message.chat.id, 'Неправильный формат ввода')
                    action(message)
        def process_name(message):
                global name
                name = message.text.strip()
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
                phone = message.text.strip()
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
                email = message.text.strip()
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
                information = message.text.strip()
            global name
            global date_of_bd
            global phone
            global email
            try:
                connection = psycopg2.connect(dbname='polluvna', user='polluvna', password='KyFPza0pFLM7',
                                              host='158.160.137.15')
                cur = connection.cursor()
                cur.execute(
                    "INSERT INTO public.users(name, date_of_bd, chat_id, phone, email, information) VALUES ('%s', to_date('%s','dd.mm.yyyy'), '%s', '%s', '%s', '%s')" % (
                name, date_of_bd, message.chat.id, phone, email, information))
                connection.commit()
                cur.close()
                connection.close()
                bot.reply_to(message, 'Добавлен пользователь: ' + name)
                action(message)
            except Exception:
                bot.send_message(message.chat.id, 'Что-то пошло не так. Попробуйте другие данные.')
                action(message)



    if callback.data == 'show bd':
        connection = psycopg2.connect(dbname='polluvna', user='polluvna', password='KyFPza0pFLM7', host='158.160.137.15')
        cur = connection.cursor()
        #@todo при падении бота переменые чистятся, и идёт в базу неправильный запрос
        #user_id_tg = callback.message.from_user.id
        message_chat_id = callback.message.chat.id

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

bot.infinity_polling()

