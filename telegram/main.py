import telebot
from dotenv import dotenv_values

from utils import add, get_record, remove

config = dotenv_values(".env")

bot = telebot.TeleBot(config.get("BOT_TOKEN"))

@bot.message_handler(commands=['start'])
def handle_start(message):
    user = message.from_user

    user_id = user.id
    first_name = user.first_name
    last_name = user.last_name
    username = user.username

    # Gửi tin nhắn chào hỏi với thông tin về người dùng
    bot.reply_to(message, f"Hi {first_name} {last_name} ({username})! Your user ID is {user_id}.")

@bot.message_handler(commands=['add'])
def handle_add(message):
    add(bot, message)
@bot.message_handler(commands=['remove'])
def handle_add(message):
    remove(bot, message)
@bot.message_handler(commands=['get'])
def handle_add(message):
    get_record(bot, message)
if __name__ == '__main__':
    bot.infinity_polling()
