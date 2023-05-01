import sqlite3
from typing import Optional, Tuple
from src.game.GameState import GameState
from src import config
from src.db import types


class DBConnection:
    def __init__(self):
        self.__connection = sqlite3.connect(config.DB_URL, check_same_thread=False)

    def __del__(self):
        self.__connection.close()

    def get_player_game(self, player: types.Player) -> Optional[GameState]:
        cursor = self.__connection.execute("""SELECT game_state FROM Games
            WHERE first_player = $1 OR second_player = $1""", (player.chat_id,))
        row = cursor.fetchone()
        return GameState(row[0]) if row else None

    def find_opponent(self, player: types.Player) -> Optional[types.Player]:
        cursor = self.__connection.execute("SELECT * FROM WaitingPlayers WHERE chat_id != $1 LIMIT 1",
                                           (player.chat_id,))
        player_data = cursor.fetchone()
        if player_data is None:
            return None
        return types.Player(*player_data)

    def add_waiting_player(self, player: types.Player):
        self.__connection.execute("INSERT INTO WaitingPlayers VALUES ($1, $2)",
                                  (player.chat_id, player.username))

    def remove_waiting_player(self, player: types.Player):
        self.__connection.execute("DELETE FROM WaitingPlayers WHERE chat_id = $1", (player.chat_id,))

    def check_player_waiting(self, player: types.Player) -> bool:
        cursor = self.__connection.execute("SELECT * FROM WaitingPlayers WHERE chat_id = $1", (player.chat_id,))
        return cursor.fetchone() is not None

    def start_game(self, first: types.Player, second: types.Player):
        self.__connection.execute("DELETE FROM WaitingPlayers WHERE chat_id = $1 OR chat_id = $2",
                                  (first.chat_id, second.chat_id))
        self.__connection.execute("INSERT INTO Games VALUES ($1, $2, $3)",
                                  (first.chat_id, second.chat_id, config.START_POSITION_CODE))
