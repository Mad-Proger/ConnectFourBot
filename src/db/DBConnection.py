import sqlite3
from typing import Optional
from src.game.GameState import GameState
from src import config


class DBConnection:
    def __init__(self):
        self.__connection = sqlite3.connect(config.DB_URL, check_same_thread=False)

    def __del__(self):
        self.__connection.close()

    def get_player_game(self, player_id: int) -> Optional[GameState]:
        cursor = self.__connection.execute("""SELECT game_state FROM Games
            WHERE first_player = $1 OR second_player = $1""", (player_id,))
        row = cursor.fetchone()
        return GameState(row[0]) if row else None

    def get_player_opponent(self, player_id: int) -> int:
        cursor = self.__connection.execute("""SELECT first_player, second_player FROM Games
            WHERE first_player = $1 OR second_player = $1""", (player_id,))
        row = cursor.fetchone()
        return row[0] if row[0] != player_id else row[1]

    def find_opponent(self, player_id: int) -> Optional[int]:
        cursor = self.__connection.execute("SELECT * FROM WaitingPlayers WHERE chat_id != $1 LIMIT 1",
                                           (player_id,))
        player_data = cursor.fetchone()
        return player_data[0] if player_data is not None else None

    def add_waiting_player(self, player_id: int):
        self.__connection.execute("INSERT INTO WaitingPlayers VALUES ($1)",
                                  (player_id,))

    def remove_waiting_player(self, player_id: int):
        self.__connection.execute("DELETE FROM WaitingPlayers WHERE chat_id = $1",
                                  (player_id,))

    def check_player_waiting(self, player_id: int) -> bool:
        cursor = self.__connection.execute("SELECT * FROM WaitingPlayers WHERE chat_id = $1",
                                           (player_id,))
        return cursor.fetchone() is not None

    def start_game(self, first: int, second: int):
        self.__connection.execute("DELETE FROM WaitingPlayers WHERE chat_id = $1 OR chat_id = $2",
                                  (first, second))
        self.__connection.execute("INSERT INTO Games VALUES ($1, $2, $3)",
                                  (first, second, config.START_POSITION_CODE))

    def update_game(self, player_id: int, game_state: GameState):
        self.__connection.execute("UPDATE Games SET game_state = $1 WHERE first_player = $2 OR second_player = $2",
                                  (game_state.get_code(), player_id))
