import telebot
from src.bot import config
from src.db import query_wrapper

bot_instance = telebot.TeleBot(token=config.BOT_TOKEN)


@bot_instance.message_handler(commands=["start", "help"])
def greet(message: telebot.types.Message):
    bot_instance.send_message(message.chat.id, "Greetings from ConnectFourBot")


@bot_instance.message_handler(commands=["find_game"])
def find_game(message: telebot.types.Message):
    opponent_info = query_wrapper.find_opponent(message.chat.id)
    if opponent_info is None:
        bot_instance.send_message(message.chat.id, "Waiting for your opponent")
        query_wrapper.add_waiting_player(message.chat.id, message.chat.username)
        return

    chat_id, username = opponent_info
    bot_instance.send_message(message.chat.id, f"Your opponent is {username}")
    query_wrapper.remove_waiting_player(chat_id)
