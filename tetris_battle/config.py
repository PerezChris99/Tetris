# Game Configuration
import pygame

# Screen dimensions
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700
GRID_WIDTH = 10
GRID_HEIGHT = 20
CELL_SIZE = 30

# Player grids positioning
PLAYER_GRID_X = 150
PLAYER_GRID_Y = 100
AI_GRID_X = 650
AI_GRID_Y = 100

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (64, 64, 64)

# Tetromino colors
COLORS = {
    'I': (0, 255, 255),    # Cyan
    'O': (255, 255, 0),    # Yellow
    'T': (255, 0, 255),    # Magenta
    'S': (0, 255, 0),      # Green
    'Z': (255, 0, 0),      # Red
    'J': (0, 0, 255),      # Blue
    'L': (255, 165, 0),    # Orange
    'GHOST': (100, 100, 100)  # Ghost piece
}

# Game timing
FALL_TIME = 1000  # milliseconds
FAST_FALL_TIME = 50
LOCK_DELAY = 500
AI_MOVE_DELAY = 500

# UI colors
UI_BACKGROUND = (30, 30, 40)
UI_TEXT = (255, 255, 255)
UI_ACCENT = (100, 200, 255)

# Round settings
MAX_ROUNDS = 5
ROUNDS_TO_WIN = 3
ROUND_TIME_LIMIT = 120  # seconds

# AI difficulty settings
AI_THINK_TIME = 0.3  # seconds to "think" before making a move

# Font sizes
FONT_LARGE = 48
FONT_MEDIUM = 24
FONT_SMALL = 16
