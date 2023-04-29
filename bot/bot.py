import telebot
from bot import config


bot_instance = telebot.TeleBot(token=config.BOT_TOKEN)


@bot_instance.message_handler(commands=["start", "help"])
def greet(message: telebot.types.Message):
    bot_instance.send_message(message.chat.id, "Greetings from ConnectFourBot")
