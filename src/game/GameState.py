import enum
from typing import Optional
from src import config


class TokenColor(enum.Enum):
    RED = "r"
    YELLOW = "y"


class GameState:
    DIRECTION_VECTORS = ((1, 0), (1, 1), (0, 1), (-1, 0))

    def __init__(self, code: int = config.START_POSITION_CODE):
        self.__columns = [[] for _ in range(7)]
        total_tokens = 0
        for col in range(7):
            mask = (1 << 7) - 1
            bit_shift = 7 * col
            column_code = (code & (mask << bit_shift)) >> bit_shift
            cnt_tokens = 6
            while column_code & (1 << cnt_tokens) == 0:
                cnt_tokens -= 1
            total_tokens += cnt_tokens
            for i in range(cnt_tokens):
                self.__columns[col].append(TokenColor.YELLOW if (column_code & (1 << i)) != 0
                                           else TokenColor.RED)
        self.__current_color = TokenColor.YELLOW if total_tokens % 2 == 0 else TokenColor.RED

    def get_code(self) -> int:
        res = 0
        for column in range(7):
            for row, token in enumerate(self.__columns[column]):
                if token == TokenColor.YELLOW:
                    res |= 1 << (7 * column + row)
            res |= 1 << (7 * column + len(self.__columns[column]))
        return res

    def place_token(self, column: int):
        if column not in range(7) or len(self.__columns[column]) == 6:
            raise IndexError

        self.__columns[column].append(self.__current_color)
        self.__change_player()

    def __change_player(self):
        self.__current_color = TokenColor.RED if self.__current_color == TokenColor.YELLOW else TokenColor.YELLOW

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

    def __str__(self):
        return "\n".join("".join("🔵" if line >= len(self.__columns[col]) else
                                 "🟡" if self.__columns[col][line] == TokenColor.YELLOW else "🔴"
                                 for col in range(7))
                         for line in range(5, -1, -1))
