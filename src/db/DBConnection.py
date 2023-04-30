import sqlite3
from typing import Optional, Tuple
from src.game.GameState import GameState
from src import config


class DBConnection:
    def __init__(self):
        self.__connection = sqlite3.connect(config.DB_URL, check_same_thread=False)

    def __del__(self):
        self.__connection.close()

    def get_player_name(self, player_id: int) -> Optional[GameState]:
        cursor = self.__connection.execute("""SELECT game_state FROM Games 
            WHERE first_player = $1 OR second_player = $1""", (player_id,))
        row = cursor.fetchone()
        return row[0] if row else None

    def find_opponent(self, chat_id: int) -> Tuple[int, str]:
        cursor = self.__connection.execute("SELECT * FROM WaitingPlayers WHERE chat_id != $1 LIMIT 1", (chat_id,))
        return cursor.fetchone()

    def add_waiting_player(self, chat_id: int, username: str):
        self.__connection.execute("INSERT INTO WaitingPlayers VALUES ($1, $2)", (chat_id, username))

    def remove_waiting_player(self, chat_id: int):
        self.__connection.execute("DELETE FROM WaitingPlayers WHERE chat_id = $1", (chat_id,))
