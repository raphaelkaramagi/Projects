import pygame

# Screen dimensions
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800
BOARD_SIZE = 640
SQUARE_SIZE = BOARD_SIZE // 8

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (200, 200, 200)
LIGHT_SQUARE = (240, 217, 181)
DARK_SQUARE = (181, 136, 99)
HIGHLIGHT = (255, 255, 0)
BEST_MOVE_COLOR = (0, 255, 0)

# Font
DEFAULT_FONT = None
DEFAULT_FONT_SIZE = 24
TITLE_FONT_SIZE = 36
LARGE_FONT_SIZE = 48

# Engine settings
STOCKFISH_PATH = "stockfish"
ENGINE_THREADS = 1
ENGINE_HASH = 16

# Difficulty settings
DIFFICULTY_SETTINGS = {
    "easy": {"skill_level": 0, "time": 0.01, "depth": 1},
    "medium": {"skill_level": 10, "time": 0.1, "depth": 3},
    "hard": {"skill_level": 20, "time": 1.0, "depth": 5}
}

# Evaluation settings
EVAL_TIME = 0.5
EVAL_DEPTH = 20
EVAL_PV_LINE_LENGTH = 5 