import pygame
import time
import random
from tetromino import Tetromino, GameBoyRandomizer
from config import *

class TetrisGame:
    def __init__(self, start_level=0, game_type="A-TYPE", sound_manager=None):
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.grid_colors = [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.generator = GameBoyRandomizer()
        self.current_piece = None
        self.next_piece = None
        self.score = 0
        self.lines_cleared = 0
        self.pieces_dropped = 0  # Track pieces dropped for statistics
        self.level = start_level
        self.start_level = start_level
        self.game_type = game_type
        self.sound_manager = sound_manager
        self.fall_time = frames_to_ms(GRAVITY_TABLE[min(self.level, MAX_LEVEL)])
        self.last_fall = 0
        self.game_over = False
        self.lines_needed = self._calculate_lines_needed()
        
        # Line clearing animation state
        self.clearing_lines = []
        self.clear_animation_timer = 0
        self.clear_animation_duration = frames_to_ms(5)  # 5 frames for clearing animation (Game Boy authentic)
        self.clear_animation_active = False
        
        self.spawn_new_piece()
        
    def _calculate_lines_needed(self):
        """Calculate lines needed for next level - Game Boy Tetris style
        
        A-Type: Level progression is every 10 lines:
        - Level 0: 0-9 lines (needs 10 lines to reach level 1)
        - Level 1: 10-19 lines (needs 10 more lines to reach level 2)
        - Level 2: 20-29 lines (needs 10 more lines to reach level 3)
        - etc.
        B-Type: No level progression (fixed 25 lines to clear)
        """
        if self.game_type == "B-TYPE":
            return 25  # B-Type is always 25 lines
        
        # For A-Type, each level needs 10 lines
        return (self.level + 1) * 10
    
    def spawn_new_piece(self):
        """Spawn a new piece at the top of the grid - Game Boy style"""
        self.current_piece = self.generator.get_next()
        self.next_piece = self.generator.current_piece
        
        # Game Boy authentic spawn positions
        piece_type = self.current_piece.shape_type
        
        if piece_type == 'I':
            # I-piece spawns at column 3, row 0 (centered)
            self.current_piece.x = 3
            self.current_piece.y = 0
        elif piece_type == 'O':
            # O-piece spawns at column 4, row 0 (slightly right of center)
            self.current_piece.x = 4
            self.current_piece.y = 0
        elif piece_type in ['T', 'S', 'Z', 'J', 'L']:
            # T, S, Z, J, L pieces spawn at column 3, row 0 (centered)
            self.current_piece.x = 3
            self.current_piece.y = 0
        else:
            # Default fallback
            self.current_piece.x = 3
            self.current_piece.y = 0
        
        # Check if the new piece can be placed (Game Over condition)
        if self.check_collision(self.current_piece):
            self.game_over = True
            return False
        
        return True
    
    def check_collision(self, piece, dx=0, dy=0):
        """Check if piece would collide at the given offset"""
        for block_x, block_y in piece.get_blocks():
            new_x = block_x + dx
            new_y = block_y + dy
            
            # Check boundaries
            if new_x < 0 or new_x >= GRID_WIDTH or new_y >= GRID_HEIGHT:
                return True
            
            # Check collision with placed blocks (ignore blocks above the grid)
            if new_y >= 0 and self.grid[new_y][new_x] != 0:
                return True
        
        return False
    
    def move_piece(self, dx, dy):
        """Move the current piece by the given offset"""
        if not self.current_piece or self.game_over:
            return False
        
        if not self.check_collision(self.current_piece, dx, dy):
            self.current_piece.x += dx
            self.current_piece.y += dy
            return True
        return False
    
    def rotate_piece(self):
        """Rotate the current piece - Game Boy style (no wall kicks)"""
        if not self.current_piece or self.game_over:
            return False
        
        # Try rotation
        original_rotation = self.current_piece.rotation
        self.current_piece.rotate()
        
        # Check if rotation is valid (no wall kicks in Game Boy Tetris)
        if not self.check_collision(self.current_piece):
            return True
        
        # Rotation failed, revert
        self.current_piece.rotation = original_rotation
        return False
    
    def soft_drop(self):
        """Soft drop - Game Boy Tetris style (1/3 of normal gravity, ~0.19s per cell)"""
        if not self.current_piece or self.game_over:
            return 0
        
        drop_distance = 0
        if not self.check_collision(self.current_piece, 0, 1):
            self.current_piece.y += 1
            drop_distance = 1
            # Award 1 point per cell dropped (Game Boy authentic)
            self.score = min(self.score + SOFT_DROP_POINTS, MAX_SCORE)
        else:
            # Piece has landed, lock it immediately (no lock delay in Game Boy)
            self.lock_piece()
        
        return drop_distance
    
    def lock_piece(self):
        """Lock the current piece into the grid"""
        if not self.current_piece:
            return
        
        # Place the piece on the grid
        for block_x, block_y in self.current_piece.get_blocks():
            if 0 <= block_x < GRID_WIDTH and 0 <= block_y < GRID_HEIGHT:
                self.grid[block_y][block_x] = 1
                self.grid_colors[block_y][block_x] = self.current_piece.color
        
        # Increment pieces dropped counter
        self.pieces_dropped += 1
        
        # Check for line clears
        lines_cleared = self.clear_lines()
        if lines_cleared > 0:
            # Don't update score or spawn new piece until animation completes
            return
        
        # Spawn new piece immediately if no lines cleared
        self.spawn_new_piece()
    
    def finish_line_clear(self):
        """Finish line clearing after animation"""
        lines_cleared = self.complete_line_clear()
        if lines_cleared > 0:
            self.update_score(lines_cleared)
            self.update_level()
        
        # Spawn new piece after clearing
        self.spawn_new_piece()
    
    def clear_lines(self):
        """Clear completed lines and return the number cleared - Game Boy style"""
        lines_to_clear = []
        
        # Find completed lines
        for row in range(GRID_HEIGHT):
            if all(self.grid[row][col] != 0 for col in range(GRID_WIDTH)):
                lines_to_clear.append(row)
        
        if lines_to_clear:
            # Start line clearing animation
            self.clearing_lines = lines_to_clear
            self.clear_animation_timer = 0
            self.clear_animation_active = True
            return len(lines_to_clear)
        
        return 0
    
    def complete_line_clear(self):
        """Complete the line clearing after animation"""
        if not self.clearing_lines:
            return
        
        # Remove completed lines
        for row in reversed(self.clearing_lines):
            del self.grid[row]
            del self.grid_colors[row]
            # Add new empty line at top
            self.grid.insert(0, [0 for _ in range(GRID_WIDTH)])
            self.grid_colors.insert(0, [BLACK for _ in range(GRID_WIDTH)])
        
        lines_cleared = len(self.clearing_lines)
        self.lines_cleared += lines_cleared
        
        # Reset animation state
        self.clearing_lines = []
        self.clear_animation_active = False
        
        return lines_cleared
    
    def update_score(self, lines_cleared):
        """Update score using Game Boy BPS scoring system"""
        if lines_cleared > 0:
            base_score = SCORE_VALUES.get(lines_cleared, 0)
            level_multiplier = self.level + 1
            points = base_score * level_multiplier
            self.score = min(self.score + points, MAX_SCORE)
            
            # Play line clear sound
            if self.sound_manager and hasattr(self.sound_manager, 'play_sound'):
                self.sound_manager.play_sound('clear')
    
    def update_level(self):
        """Update level based on lines cleared - Game Boy Tetris style"""
        if self.level < MAX_LEVEL:
            new_level = self.lines_cleared // 10
            if new_level > self.level:
                self.level = new_level
                self.lines_needed = self._calculate_lines_needed()
                # Update fall speed using Game Boy gravity table
                self.fall_time = frames_to_ms(GRAVITY_TABLE[min(self.level, MAX_LEVEL)])
                print(f"Level up! Now level {self.level}, next level at {self.lines_needed} lines")
    
    def update(self, dt):
        """Update game state"""
        if self.game_over:
            return
        
        current_time = pygame.time.get_ticks()
        
        # Handle line clearing animation
        if self.clear_animation_active:
            self.clear_animation_timer += dt * 1000  # Convert to milliseconds
            if self.clear_animation_timer >= self.clear_animation_duration:
                self.finish_line_clear()
            return  # Don't update falling pieces during animation
        
        # Handle piece falling
        if current_time - self.last_fall >= self.fall_time:
            if self.current_piece:
                if not self.check_collision(self.current_piece, 0, 1):
                    self.current_piece.y += 1
                else:
                    # Piece has landed, lock immediately (no lock delay in Game Boy)
                    self.lock_piece()
            self.last_fall = current_time
    
    def get_ghost_piece(self):
        """Get ghost piece position"""
        if not self.current_piece:
            return None
        
        ghost = self.current_piece.copy()
        while not self.check_collision(ghost, 0, 1):
            ghost.y += 1
        
        return ghost
    
    def get_grid_state(self):
        """Get current grid state for AI"""
        return [row[:] for row in self.grid]
    
    def simulate_placement(self, piece, x, y, rotation):
        """Simulate placing a piece and return the resulting grid state"""
        # Create a copy of the grid
        test_grid = [row[:] for row in self.grid]
        
        # Create piece at specified position and rotation
        test_piece = piece.copy()
        test_piece.x = x
        test_piece.y = y
        test_piece.rotation = rotation
        
        # Drop the piece
        while not self.check_collision_on_grid(test_piece, test_grid, 0, 1):
            test_piece.y += 1
        
        # Place the piece
        for block_x, block_y in test_piece.get_blocks():
            if 0 <= block_x < GRID_WIDTH and 0 <= block_y < GRID_HEIGHT:
                test_grid[block_y][block_x] = 1
        
        # Clear lines and count them
        lines_cleared = 0
        row = GRID_HEIGHT - 1
        while row >= 0:
            if all(test_grid[row][col] != 0 for col in range(GRID_WIDTH)):
                del test_grid[row]
                test_grid.insert(0, [0 for _ in range(GRID_WIDTH)])
                lines_cleared += 1
            else:
                row -= 1
        
        return test_grid, lines_cleared
    
    def check_collision_on_grid(self, piece, grid, dx=0, dy=0):
        """Check collision on a specific grid"""
        for block_x, block_y in piece.get_blocks():
            new_x = block_x + dx
            new_y = block_y + dy
            
            if new_x < 0 or new_x >= GRID_WIDTH or new_y >= GRID_HEIGHT:
                return True
            
            if new_y >= 0 and grid[new_y][new_x] != 0:
                return True
        
        return False
    
    def reset(self):
        """Reset the game state"""
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.grid_colors = [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.generator = GameBoyRandomizer()
        self.current_piece = None
        self.next_piece = None
        self.score = 0
        self.lines_cleared = 0
        self.pieces_dropped = 0
        self.level = self.start_level
        self.fall_time = frames_to_ms(GRAVITY_TABLE[min(self.level, MAX_LEVEL)])
        self.last_fall = 0
        self.game_over = False
        self.lines_needed = self._calculate_lines_needed()
        
        # Reset animation state
        self.clearing_lines = []
        self.clear_animation_timer = 0
        self.clear_animation_active = False
        
        self.spawn_new_piece()
    
    def send_garbage_lines(self, lines_cleared):
        """Send garbage lines to opponent based on Game Boy Tetris rules"""
        if lines_cleared == 2:  # Double
            return 1
        elif lines_cleared == 3:  # Triple
            return 2
        elif lines_cleared == 4:  # Tetris
            return 4
        else:
            return 0  # Single lines don't send garbage in Game Boy Tetris
    
    def receive_garbage_lines(self, num_lines):
        """Receive garbage lines from opponent - Game Boy style"""
        if self.game_over or num_lines <= 0:
            return
        
        # Remove lines from top to make room
        for _ in range(num_lines):
            if len(self.grid) > 0:
                self.grid.pop(0)
                self.grid_colors.pop(0)
        
        # Add garbage lines at bottom
        for _ in range(num_lines):
            # Game Boy garbage lines have a shared hole pattern
            garbage_line = [1] * GRID_WIDTH
            garbage_color_line = [GB_DARK_GRAY] * GRID_WIDTH
            
            # Add a hole (Game Boy uses shared hole positions)
            hole_position = random.randint(0, GRID_WIDTH - 1)
            garbage_line[hole_position] = 0
            garbage_color_line[hole_position] = BLACK
            
            self.grid.append(garbage_line)
            self.grid_colors.append(garbage_color_line)
    
    def check_lines_win_condition(self):
        """Check if player has cleared enough lines to win (Game Boy: 30 lines)"""
        return self.lines_cleared >= LINES_TO_WIN
