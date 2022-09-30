import telebot
import tokens
import re
import database as db
from telebot import types

global database
database = db.Database()

bot=telebot.TeleBot(tokens.address['token'])

@bot.message_handler(commands=['start'])
def send_welcome(message):
	markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
	item1 = types.KeyboardButton('Текущие показания')
	item2,item3,item4 = types.KeyboardButton('Статистика'),types.KeyboardButton('Показания за период'),types.KeyboardButton('Напомнить Никите о надобности передать показания')
	markup.add(item1,item2,item3,item4)
	bot.send_message(message.chat.id,f'Привет,{message.from_user.first_name}!\nЯ бот для хранения и подачи показаний',reply_markup=markup)
@bot.message_handler(commands=['neit'])
def button_message(message):
	markup_admin=types.ReplyKeyboardMarkup(resize_keyboard=True)

	item1 = types.KeyboardButton('Добавить показания электроэнергии')

	item2 = types.KeyboardButton('Добавить воду')
	markup_admin.row(item1,item2)
	bot.send_message(message.chat.id,'Admin ready',reply_markup=markup_admin)



@bot.message_handler(chat_types=["private"], func=lambda msg: msg.text == "Статистика")
def check_statistic(message):
    mess = bot.send_message(message.chat.id, 'За какой период вы хотите статистику?',reply_markup = create_markup(2))
    @bot.callback_query_handler(func=lambda call: True)
    def button_callback(call):
        if str.isnumeric(call.data):
            statistic = database.analytics(int(call.data))
            bot.send_message(call.message.chat.id,statistic)
            bot.send_photo(call.message.chat.id,open('Photo_stat.png','rb'))
            database.del_photo()
        else:
            bot.send_message(call.message.chat.id,call.data)

            
@bot.message_handler(chat_types=["private"], func=lambda msg: msg.text == "Текущие показания")
def last_month(message):
    bot.send_message(message.chat.id,database.prints(1))


@bot.message_handler(chat_types=["private"], func=lambda msg: msg.text == "Показания за период")
def several_month(message):
    mess = bot.send_message(message.chat.id, 'За какой период вы хотите посмотреть показания?',reply_markup = create_markup(1))
    @bot.callback_query_handler(func=lambda call: True)
    def button_callback(call):
        if str.isnumeric(call.data):	
            bot.send_message(call.message.chat.id,database.prints(int(call.data)))
        else:
        	bot.send_message(call.message.chat.id,call.data)


@bot.message_handler(chat_types=["private"], func=lambda msg: msg.text == "Добавить воду")
def add_wather(message):
    mesg = bot.send_message(message.chat.id,'Введите показания воды через пробел по следующей формме:\nГ___(пробел)Х___')
    bot.register_next_step_handler(mesg,water)


@bot.message_handler(chat_types=["private"], func=lambda msg: msg.text == "Добавить показания электроэнергии")
def add_wather(message):
    mesg = bot.send_message(message.chat.id,'Введите показания электросчетчика через пробел по следующей формме:\nТ1___(пробел)Т2___')
    bot.register_next_step_handler(mesg,electricity)
@bot.message_handler(chat_types = ["private"],func =  lambda msg: msg.text == "Напомнить Никите о надобности передать показания")
def update_db(message):
    database.mauns_update()
    bot.send_message(870048401,'База данных обновлена!\n\n\nПора передавать показания!')



def plots(message):
	statistic = database.analytics(int(message.text))
	bot.send_message(message.chat.id,statistic)
	bot.send_photo(message.chat.id,open('Photo_stat.png','rb'))
	database.del_photo()
    

def water(message):
	Water = list(map(float,re.findall(r'(\d+[.]{1}\d{3})\s*',message.text)))
	if len(Water)==2:
		database.add_firewather(Water[0])
		database.add_cullwather(Water[1])
		bot.send_message(message.chat.id,f'Добывлено\nГорячая вода: {Water[0]}\nХолодная вода: {Water[1]}')
	else:
		msg = bot.send_message(message.chat.id,'Проверьте правильность введенных данных и повторите ввод')
		bot.register_next_step_handler(msg,water)

def electricity(message):
	electricity = list(map(float,re.findall(r'(\d+[.]{1}\d{2})\s*',message.text)))
	if len(electricity) == 2:
		database.add_tone(electricity[0])
		database.add_ttwo(electricity[1])
		bot.send_message(message.chat.id,f'Добавлено:\nT1: {electricity[0]}\nT2: {electricity[1]}')
	else:
		msg = bot.send_message(message.chat.id,'Проверьте правильность введенных данных и повторите ввод')
		bot.register_next_step_handler(msg,electricity)

def create_markup(n=1,db = database.last_number):
    markup = types.InlineKeyboardMarkup()
    line1_list_mouns = {}
    line2_list_mouns = {}
    line3_list_mouns = {}
    not_in_database = u"\u274C"
    for i in range(4//n):
        formul1 = 1+3*i
        formul2 = 2+3*i
        formul3 = 3+3*i
        markup.row(types.InlineKeyboardButton(text = f'{f"{formul1} месяц(ев)" if formul1 <= db else f"{not_in_database}"}',callback_data=f'{formul1}' if formul1 <= db else 'Столько месяцев нет в базе данных'),
        types.InlineKeyboardButton(text = f'{f"{formul2} месяц(ев)" if formul2 <= db else f"{not_in_database}"}',callback_data=f'{formul2}' if formul2 <= db else 'Столько месяцев нет в базе данных'),
        types.InlineKeyboardButton(text = f'{f"{formul3} месяц(ев)" if formul3 <= db else f"{not_in_database}"}',callback_data=f'{formul3}' if formul3 <= db else 'Столько месяцев нет в базе данных'))
    return markup

def main():
    bot.infinity_polling()


if __name__ == "__main__":
    main()