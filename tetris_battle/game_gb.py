import pygame
import time
from tetromino import Tetromino, GameBoyRandomizer
from config import *

class TetrisGame:
    def __init__(self, start_level=0, game_type="A-TYPE"):
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.grid_colors = [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.generator = GameBoyRandomizer()
        self.current_piece = None
        self.next_piece = None
        self.score = 0
        self.lines_cleared = 0
        self.level = start_level
        self.start_level = start_level
        self.game_type = game_type
        self.fall_time = frames_to_ms(GRAVITY_TABLE[min(self.level, MAX_LEVEL)])
        self.last_fall = 0
        self.game_over = False
        self.lines_needed = self._calculate_lines_needed()
        self.spawn_new_piece()
        
    def _calculate_lines_needed(self):
        """Calculate lines needed for next level - Game Boy style"""
        if self.level == self.start_level:
            return self.start_level * 10 + 10
        else:
            return LINES_PER_LEVEL
    
    def spawn_new_piece(self):
        """Spawn a new piece at the top of the grid"""
        if self.current_piece is None:
            self.current_piece = self.generator.get_next()
            self.next_piece = self.generator.current_piece
        else:
            self.current_piece = Tetromino(self.next_piece)
            self.next_piece = self.generator.current_piece
        
        # Spawn at proper Game Boy position (row 17 for highest block)
        self.current_piece.x = 3
        self.current_piece.y = -1  # Start above visible area
        
        # Check if the new piece can be placed
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
        """Soft drop - faster falling, awards points"""
        if not self.current_piece or self.game_over:
            return 0
        
        drop_distance = 0
        if not self.check_collision(self.current_piece, 0, 1):
            self.current_piece.y += 1
            drop_distance = 1
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
        
        # Clear lines and update score
        lines_cleared = self.clear_lines()
        if lines_cleared > 0:
            self.update_score(lines_cleared)
            self.update_level()
        
        # Spawn new piece
        self.spawn_new_piece()
    
    def clear_lines(self):
        """Clear completed lines and return the number cleared"""
        lines_to_clear = []
        
        # Find completed lines
        for row in range(GRID_HEIGHT):
            if all(self.grid[row][col] != 0 for col in range(GRID_WIDTH)):
                lines_to_clear.append(row)
        
        # Remove completed lines
        for row in reversed(lines_to_clear):
            del self.grid[row]
            del self.grid_colors[row]
            # Add new empty line at top
            self.grid.insert(0, [0 for _ in range(GRID_WIDTH)])
            self.grid_colors.insert(0, [BLACK for _ in range(GRID_WIDTH)])
        
        self.lines_cleared += len(lines_to_clear)
        return len(lines_to_clear)
    
    def update_score(self, lines_cleared):
        """Update score using Game Boy BPS scoring system"""
        if lines_cleared > 0:
            base_score = SCORE_VALUES.get(lines_cleared, 0)
            level_multiplier = self.level + 1
            points = base_score * level_multiplier
            self.score = min(self.score + points, MAX_SCORE)
    
    def update_level(self):
        """Update level based on lines cleared - Game Boy style"""
        if self.level < MAX_LEVEL:
            if self.lines_cleared >= self.lines_needed:
                self.level += 1
                self.lines_needed = LINES_PER_LEVEL  # 10 lines per level after first
                # Update fall speed
                self.fall_time = frames_to_ms(GRAVITY_TABLE[min(self.level, MAX_LEVEL)])
    
    def update(self, dt):
        """Update game state"""
        if self.game_over:
            return
        
        current_time = pygame.time.get_ticks()
        
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
        self.level = self.start_level
        self.fall_time = frames_to_ms(GRAVITY_TABLE[min(self.level, MAX_LEVEL)])
        self.last_fall = 0
        self.game_over = False
        self.lines_needed = self._calculate_lines_needed()
        self.spawn_new_piece()
