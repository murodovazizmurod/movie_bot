import telebot
from telebot import types
import requests

bot = telebot.TeleBot('1893127985:AAHhN652ViVEGLGls9ANQ3P2S1foOBhOZb4')


def get_search(text, page):
    with requests.Session() as session:
        return session.get('https://api.themoviedb.org/3/search/movie?api_key=844dba0bfd8f3a4f3799f6130ef9e335&language=en-EN&query='+text+'&page='+str(page))
        

def get_movie(id):
    with requests.Session() as session:
        return session.get(f'https://api.themoviedb.org/3/movie/{id}?api_key=844dba0bfd8f3a4f3799f6130ef9e335&language=en-EN')


def get_movie_videos(id):
    with requests.Session() as session:
        return session.get(f'https://api.themoviedb.org/3/movie/{id}/videos?api_key=844dba0bfd8f3a4f3799f6130ef9e335&language=en-EN')


def get_popular(page):
    with requests.Session() as session:
        return session.get(f'https://api.themoviedb.org/3/movie/popular?api_key=844dba0bfd8f3a4f3799f6130ef9e335&language=en-US&page='+str(page))


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [('Find Movie', 'find'), ('Popular 🔥', 'popular#1'), ("Upcomings (In dev)", 'upcoming')]
    for i in buttons:
        markup.add(types.InlineKeyboardButton(i[0], callback_data=i[1]))
    bot.send_message(message.chat.id, "Hello! This bot for finding movies :)", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data == 'find':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='OK. Send me movie name: \n\nSend /cancel to cancel.')
        bot.register_next_step_handler_by_chat_id(call.message.chat.id, find)
    elif call.data.startswith('popular#'):
        page = call.data.split('#')[1]
        bot.answer_callback_query(call.id, "Fetching data...")
        result = get_popular(page)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text='Next Page (In Dev)', callback_data=f'find_next'))
        if result.status_code == 200:
            text = f'Results in page {result.json()["page"]}:\n\n'
            for i in result.json()['results']:
                text += f'👉 <b>{i["title"]}</b> <i>({i["original_title"]})</i> /m{i["id"]}\n\n'
            bot.send_message(call.message.chat.id, f'{text}', parse_mode='HTML', reply_markup=markup)
        else:
            bot.send_message(call.message.chat.id, "Sorry, movie that you looking for not found :/", parse_mode='HTML')
    elif call.data.startswith('videos#'):
        bot.answer_callback_query(call.id, "Fetching data...")
        id = call.data.split('#')[1]
        movie = get_movie(id)
        result = get_movie_videos(id)
        if movie.status_code == 200 and result.status_code == 200:
            text = f'{movie.json()["title"]} Videos: \n\n\n'
            for i in result.json()['results']:
                text += f'<a href="https://www.youtube.com/watch?v={i["key"]}">{i["name"]} ({i["size"]})</a> - {i["type"]}\n\n'
            text += f'To go movie page send /m{id}'
            bot.edit_message_text(text=text, parse_mode='HTML', message_id=call.message.message_id, chat_id=call.message.chat.id, disable_web_page_preview=True)
    elif call.data.startswith('find_next'):
        bot.answer_callback_query(call.id, 'In Progess...')


    
def find(message):
    if message.text == '/cancel':
        bot.clear_step_handler_by_chat_id(message.chat.id)
        start(message)
    else:
        bot.send_message(chat_id=message.chat.id, text="Fetching data ...")
        result = get_search(message.text, 1)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text='Next Page (In Dev)', callback_data=f'find_next'))
        if result.status_code == 200 and len(result.json()['results']) > 0:
            text = f'Results in page {result.json()["page"]}:\n\n'
            for i in result.json()['results']:
                text += f'👉 <b>{i["title"]}</b> <i>({i["original_title"]})</i> /m{i["id"]}\n\n'
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id+1)
            bot.send_message(message.chat.id, f'{text}', parse_mode='HTML', reply_markup=markup)
        else:
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id+1)
            bot.send_message(message.chat.id, "Sorry, movie that you looking for not found :/", parse_mode='HTML')





@bot.message_handler(func=lambda msg: msg.text[0] == '/' and msg.text[2:].isdecimal() and msg.text[1] == 'm')
def get_id(message):  
    id_ = message.text[2:]
    bot.send_message(chat_id=message.chat.id, text="Fetching data ...")
    result = get_movie(id_)
    if result.status_code == 200:
        _ = result.json()
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text='Videos', callback_data=f'videos#{_["id"]}'))
        genre = ''
        for i in _['genres']:
            genre += i['name'] + ' / '
        text = f"""🎬 {_['title']} ({_['original_title']})   
📅 {_['release_date']}
🌟 {_['vote_average']}
📜 {genre}

{_['overview']}<a href="http://image.tmdb.org/t/p/w500{_['backdrop_path']}">.</a>"""
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id+1)
        bot.reply_to(message, text, parse_mode='HTML', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Sorry, movie that you looking for not found :/", parse_mode='HTML')


bot.polling(none_stop=True)