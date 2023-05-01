import telebot
from src.db import DBConnection
from src.game import GameState


class BotClass(telebot.TeleBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__db = DBConnection.DBConnection()

        self.message_handler(commands=["start_game"])(self.__start_game)
        self.message_handler(commands=["cancel_search"])(self.__cancel_search)
        self.message_handler(regexp=r"\d+")(self.__parse_move)

    def __start_game(self, message: telebot.types.Message):
        player = message.chat.id
        if self.__db.get_player_game(player) is not None:
            self.send_message(player, "You cannot play multiple games at once")
            return
        if self.__db.check_player_waiting(player):
            self.send_message(player, "You are already waiting for the game. Be patient")
            return

        opponent = self.__db.find_opponent(player)
        if opponent is not None:
            self.__db.start_game(player, opponent)
            self.send_message(player, f"Opponent found. You're playing red")
            self.send_message(opponent, f"Opponent found. You're playing yellow")
            self.__query_move(opponent)
            return

        self.__db.add_waiting_player(player)
        self.send_message(player, "Waiting for opponent")

    def __cancel_search(self, message: telebot.types.Message):
        player = message.chat.id
        if not self.__db.check_player_waiting(player):
            self.send_message(player, "You are not waiting for the game currently")
            return

        self.__db.remove_waiting_player(player)
        self.send_message(player, "Game search canceled")

    def __query_move(self, player: int):
        game_state = self.__db.get_player_game(player)
        self.send_message(player, "Make your move:\n" + str(game_state))

    def __parse_move(self, message: telebot.types.Message):
        player = message.chat.id
        column = int(message.text)
        game = self.__db.get_player_game(player)
        if game is None:
            self.send_message(player, "You are not playing any game currently")
            return

        try:
            game.place_token(column)
        except IndexError:
            self.send_message(player, "Incorrect move")
        else:
            self.__db.update_game(player, game)
            opponent = self.__db.get_player_opponent(player)
            winner = game.get_winner_color()
            if winner is not None:
                winner = "First" if winner == GameState.TokenColor.YELLOW else "Second"
                self.send_message(player, f"Game finished. {winner} player is victorious")
                self.send_message(opponent, f"Game finished. {winner} player is victorious")
            else:
                self.__db.update_game(player, game)
                self.__query_move(opponent)

