import sqlite3
from typing import Optional, Tuple
from src.game.GameState import GameState

db = sqlite3.connect("data/db.sqlite3", check_same_thread=False)


def get_player_game(player_id: int) -> Optional[GameState]:
    cursor = db.execute("""SELECT game_state FROM Games 
    WHERE first_player = $1 OR second_player = $1""", (player_id,))
    row = cursor.fetchone()
    return row[0] if row else None


def find_opponent(chat_id: int) -> Tuple[int, str]:
    cursor = db.execute("SELECT * FROM WaitingPlayers WHERE chat_id != $1 LIMIT 1", (chat_id,))
    return cursor.fetchone()


def add_waiting_player(chat_id: int, username: str):
    db.execute("INSERT INTO WaitingPlayers VALUES ($1, $2)", (chat_id, username))


def remove_waiting_player(chat_id: int):
    db.execute("DELETE FROM WaitingPlayers WHERE chat_id = $1", (chat_id,))
