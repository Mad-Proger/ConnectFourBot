import telebot


class BotClass(telebot.TeleBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.message_handler(commands=["start"])(self.__greet)

    def __greet(self, message: telebot.types.Message):
        self.send_message(message.chat.id, "Greetings from ConnectFourBot")
