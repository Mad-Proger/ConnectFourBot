import ctypes
from src import config
from src.game import GameState


class Solver:
    def __init__(self):
        self.__solver = ctypes.CDLL(config.COMPILED_SOLVER_PATH)

    def find_optimal_column(self, game: GameState.GameState) -> int:
        if game.moves_made() >= 10:
            return self.__solver.findBestMove(ctypes.c_longlong(game.get_code()))
        for column in range(7):
            if game.check_move(column):
                return column
