import telebot
from decouple import config

bot = telebot.TeleBot(token=config("BOT_TOKEN"))


def send_borrowing_creation_notification(user, book_title):
    bot.send_message(config("CHAT_ID"), f"{user} borrowed '{book_title}' book")
