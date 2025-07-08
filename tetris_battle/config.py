# Game Configuration - 1989 Game Boy Tetris Style
import pygame

# Screen dimensions - Game Boy style
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_WIDTH = 10
GRID_HEIGHT = 20  # 18 visible + 2 hidden rows
VISIBLE_HEIGHT = 18
CELL_SIZE = 24

# Player grids positioning
PLAYER_GRID_X = 50
PLAYER_GRID_Y = 80
AI_GRID_X = 450
AI_GRID_Y = 80

# Game Boy 4-shade palette (greenish monochrome)
GB_BLACK = (15, 56, 15)        # Darkest green
GB_DARK_GRAY = (48, 98, 48)    # Dark green
GB_LIGHT_GRAY = (139, 172, 15) # Light green
GB_WHITE = (155, 188, 15)      # Lightest green
GB_BACKGROUND = (139, 172, 15)

# Colors - Game Boy style monochrome
BLACK = GB_BLACK
WHITE = GB_WHITE
GRAY = GB_DARK_GRAY
LIGHT_GRAY = GB_LIGHT_GRAY
DARK_GRAY = GB_DARK_GRAY
BACKGROUND = GB_BACKGROUND

# All tetrominoes use same color in Game Boy style
TETROMINO_COLOR = GB_BLACK
COLORS = {
    'I': TETROMINO_COLOR,
    'O': TETROMINO_COLOR,
    'T': TETROMINO_COLOR,
    'S': TETROMINO_COLOR,
    'Z': TETROMINO_COLOR,
    'J': TETROMINO_COLOR,
    'L': TETROMINO_COLOR,
    'GHOST': GB_DARK_GRAY
}

# Game Boy Tetris gravity table (frames per row at 59.73 FPS)
GRAVITY_TABLE = {
    0: 53, 1: 49, 2: 45, 3: 41, 4: 37, 5: 33, 6: 28, 7: 22, 8: 17, 9: 11,
    10: 10, 11: 9, 12: 8, 13: 7, 14: 6, 15: 6, 16: 5, 17: 5, 18: 4, 19: 4, 20: 3
}

# Convert frames to milliseconds (59.73 FPS)
FRAME_TIME = 1000 / 59.73
def frames_to_ms(frames):
    return frames * FRAME_TIME

# Game timing - Game Boy Tetris authentic timings
SOFT_DROP_SPEED = frames_to_ms(1)  # 1 frame per row when soft dropping
DAS_DELAY = frames_to_ms(24)  # 24 frames for DAS activation (Game Boy authentic)
DAS_SPEED = frames_to_ms(10)  # 10 frames between DAS moves

# Soft drop is 1/3 of normal gravity in Game Boy (approximately 0.19 seconds per cell)
SOFT_DROP_MULTIPLIER = 3  # Soft drop is 3x faster than normal gravity

# Scoring - Game Boy Tetris BPS system
SCORE_VALUES = {
    1: 40,    # Single
    2: 100,   # Double
    3: 300,   # Triple
    4: 1200   # Tetris
}
SOFT_DROP_POINTS = 1  # Points per cell dropped
MAX_SCORE = 999999

# Level progression
MAX_LEVEL = 20
LINES_PER_LEVEL = 10  # Lines needed to advance level (after initial)

# UI colors - Game Boy style
UI_BACKGROUND = GB_BACKGROUND
UI_TEXT = GB_BLACK
UI_BORDER = GB_DARK_GRAY

# Game modes
GAME_TYPE_A = "A-TYPE"  # Marathon mode
GAME_TYPE_B = "B-TYPE"  # 25-line mode
GAME_TYPE_VS = "VS"     # 2-player mode

# Font sizes (Game Boy style - small pixelated font)
FONT_LARGE = 24
FONT_MEDIUM = 16
FONT_SMALL = 12

# Round settings (for VS mode)
MAX_ROUNDS = 5
ROUNDS_TO_WIN = 3
LINES_TO_WIN = 30  # In GB Tetris, clearing 30 lines wins a round

# Game Boy authenticity settings
SHOW_GHOST_PIECE = False  # Original Game Boy Tetris had no ghost piece
ENABLE_HARD_DROP = False  # Original Game Boy Tetris had no hard drop
AUTHENTIC_SPAWN_DELAY = True  # Use authentic spawn delays

# AI settings
AI_THINK_TIME = 0.15  # Balanced thinking time for good competition
