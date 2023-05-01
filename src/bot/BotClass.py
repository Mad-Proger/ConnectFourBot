import telebot
from src.db import DBConnection
from src.db import types


class BotClass(telebot.TeleBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__db = DBConnection.DBConnection()

        self.message_handler(commands=["start_game"])(self.__start_game)
        self.message_handler(commands=["cancel_search"])(self.__cancel_search)

    @staticmethod
    def __get_player(message: telebot.types.Message) -> types.Player:
        return types.Player(message.chat.id, message.chat.username)

    def __start_game(self, message: telebot.types.Message):
        player = self.__get_player(message)
        if self.__db.get_player_game(player) is not None:
            self.send_message(player.chat_id, "You cannot play multiple games at once")
            return
        if self.__db.check_player_waiting(player):
            self.send_message(player.chat_id, "You are already waiting for the game. Be patient")
            return

        opponent = self.__db.find_opponent(player)
        if opponent is not None:
            self.__db.start_game(player, opponent)
            self.send_message(player.chat_id, f"Your opponent is {opponent.username}. You're playing red")
            self.send_message(opponent.chat_id, f"Your opponent is {player.username}. You're playing yellow")
            self.__query_move(opponent)
            return

        self.__db.add_waiting_player(player)
        self.send_message(player.chat_id, "Waiting for opponent")

    def __cancel_search(self, message: telebot.types.Message):
        player = self.__get_player(message)
        if not self.__db.check_player_waiting(player):
            self.send_message(player.chat_id, "You are not waiting for the game currently")
            return

        self.__db.remove_waiting_player(player)
        self.send_message(player.chat_id, "Game search canceled")

    def __query_move(self, player: types.Player):
        pass
