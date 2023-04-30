import enum
from typing import Optional


class TokenColor(enum.Enum):
    RED = "r"
    YELLOW = "y"


class GameState:
    DIRECTION_VECTORS = ((1, 0), (1, 1), (0, 1), (-1, 0))

    def __init__(self):
        self.__columns = [[] for _ in range(7)]
        self.__current_color = TokenColor.YELLOW

    def place_token(self, column: int):
        if column not in range(7) or len(self.__columns[column]) == 6:
            raise IndexError

        self.__columns[column].append(self.__current_color)
        self.__change_player()

    def __change_player(self):
        self.__current_color = TokenColor.RED if self.__current_color == TokenColor.YELLOW else TokenColor.YELLOW

    def __str__(self):
        return " ".join("".join(color.value for color in column) for column in self.__columns)

    def from_string(self, s: str):
        for i, column_str in enumerate(s.split()):
            self.__columns[i] = [TokenColor(c) for c in column_str]

    def __check_in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < len(self.__columns) and 0 <= y < len(self.__columns[x])

    def __count_direction(self, x: int, y: int, dx: int, dy: int) -> int:
        color = self.__columns[x][y]
        res = 0
        while self.__check_in_bounds(x, y):
            if self.__columns[x][y] != color:
                break
            res += 1
            x += dx
            y += dy
        return res

    def __get_connected_count(self, x: int, y: int, dx: int, dy: int) -> int:
        if not self.__check_in_bounds(x, y):
            return 0
        return self.__count_direction(x, y, dx, dy) + self.__count_direction(x, y, -dx, -dy) - 1

    def get_winner_color(self) -> Optional[TokenColor]:
        for x in range(len(self.__columns)):
            for y in range(len(self.__columns[x])):
                for dx, dy in self.DIRECTION_VECTORS:
                    if self.__get_connected_count(x, y, dx, dy) >= 4:
                        return self.__columns[x][y]

    def is_finished(self) -> bool:
        return self.get_winner_color() is not None
