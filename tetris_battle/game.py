import pygame
import time
from tetromino import Tetromino, TetrominoGenerator
from config import *

class TetrisGame:
    def __init__(self):
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.grid_colors = [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.generator = TetrominoGenerator()
        self.current_piece = None
        self.next_pieces = []
        self.score = 0
        self.lines_cleared = 0
        self.level = 1
        self.fall_time = FALL_TIME
        self.last_fall = 0
        self.lock_delay_start = 0
        self.is_locking = False
        self.game_over = False
        self.spawn_new_piece()
        
    def spawn_new_piece(self):
        """Spawn a new piece at the top of the grid"""
        if not self.next_pieces:
            self.next_pieces = self.generator.peek(3)
        
        self.current_piece = self.generator.get_next()
        self.next_pieces = self.generator.peek(3)
        
        # Check if the new piece can be placed
        if self.check_collision(self.current_piece):
            self.game_over = True
            return False
        
        self.is_locking = False
        self.lock_delay_start = 0
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
            
            # Reset lock delay if moving horizontally or soft dropping
            if dx != 0 or (dy > 0 and not self.check_collision(self.current_piece, 0, 1)):
                self.is_locking = False
                self.lock_delay_start = 0
            
            return True
        return False
    
    def rotate_piece(self):
        """Rotate the current piece with wall kick attempts"""
        if not self.current_piece or self.game_over:
            return False
        
        # Simple rotation - try basic position first
        original_rotation = self.current_piece.rotation
        self.current_piece.rotate()
        
        # Check if rotation is valid
        if not self.check_collision(self.current_piece):
            self.is_locking = False
            self.lock_delay_start = 0
            return True
        
        # Try wall kicks
        kick_offsets = [(0, 0), (-1, 0), (1, 0), (0, -1), (-1, -1), (1, -1)]
        
        for dx, dy in kick_offsets:
            if not self.check_collision(self.current_piece, dx, dy):
                self.current_piece.x += dx
                self.current_piece.y += dy
                self.is_locking = False
                self.lock_delay_start = 0
                return True
        
        # Rotation failed, revert
        self.current_piece.rotation = original_rotation
        return False
    
    def hard_drop(self):
        """Drop the piece to the bottom instantly"""
        if not self.current_piece or self.game_over:
            return 0
        
        drop_distance = 0
        while not self.check_collision(self.current_piece, 0, 1):
            self.current_piece.y += 1
            drop_distance += 1
        
        self.lock_piece()
        return drop_distance
    
    def lock_piece(self):
        """Lock the current piece into the grid"""
        if not self.current_piece:
            return
        
        # Place the piece on the grid
        for block_x, block_y in self.current_piece.get_blocks():
            if block_y >= 0:  # Only place blocks that are visible
                self.grid[block_y][block_x] = 1
                self.grid_colors[block_y][block_x] = self.current_piece.color
        
        # Clear lines and update score
        lines_cleared = self.clear_lines()
        self.update_score(lines_cleared)
        
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
        for row in sorted(lines_to_clear, reverse=True):
            del self.grid[row]
            del self.grid_colors[row]
            self.grid.insert(0, [0 for _ in range(GRID_WIDTH)])
            self.grid_colors.insert(0, [BLACK for _ in range(GRID_WIDTH)])
        
        return len(lines_to_clear)
    
    def update_score(self, lines_cleared):
        """Update score and level based on lines cleared"""
        if lines_cleared > 0:
            # Tetris scoring system
            base_scores = [0, 100, 300, 500, 800]
            self.score += base_scores[min(lines_cleared, 4)] * self.level
            self.lines_cleared += lines_cleared
            
            # Level up every 10 lines
            new_level = self.lines_cleared // 10 + 1
            if new_level > self.level:
                self.level = new_level
                self.fall_time = max(50, FALL_TIME - (self.level - 1) * 50)
    
    def get_ghost_piece(self):
        """Get the ghost piece position (where the piece would land)"""
        if not self.current_piece:
            return None
        
        ghost = self.current_piece.copy()
        while not self.check_collision(ghost, 0, 1):
            ghost.y += 1
        
        return ghost
    
    def update(self, dt):
        """Update game state"""
        if self.game_over or not self.current_piece:
            return
        
        current_time = pygame.time.get_ticks()
        
        # Handle gravity
        if current_time - self.last_fall >= self.fall_time:
            if not self.move_piece(0, 1):
                # Piece can't fall, start lock delay
                if not self.is_locking:
                    self.is_locking = True
                    self.lock_delay_start = current_time
                elif current_time - self.lock_delay_start >= LOCK_DELAY:
                    self.lock_piece()
            else:
                self.is_locking = False
                self.lock_delay_start = 0
            
            self.last_fall = current_time
    
    def get_grid_state(self):
        """Get the current grid state for AI analysis"""
        # Create a copy of the grid with the current piece placed
        grid_copy = [row[:] for row in self.grid]
        
        if self.current_piece:
            for block_x, block_y in self.current_piece.get_blocks():
                if 0 <= block_x < GRID_WIDTH and 0 <= block_y < GRID_HEIGHT:
                    grid_copy[block_y][block_x] = 1
        
        return grid_copy
    
    def simulate_placement(self, piece, x, y, rotation):
        """Simulate placing a piece and return the resulting grid state"""
        # Create a copy of the current grid
        grid_copy = [row[:] for row in self.grid]
        
        # Create a copy of the piece with the specified position and rotation
        test_piece = piece.copy()
        test_piece.x = x
        test_piece.y = y
        test_piece.rotation = rotation
        
        # Drop the piece to the bottom
        while not self.check_collision_on_grid(test_piece, grid_copy, 0, 1):
            test_piece.y += 1
        
        # Place the piece on the grid
        for block_x, block_y in test_piece.get_blocks():
            if 0 <= block_x < GRID_WIDTH and 0 <= block_y < GRID_HEIGHT:
                grid_copy[block_y][block_x] = 1
        
        # Clear lines
        lines_cleared = 0
        row = GRID_HEIGHT - 1
        while row >= 0:
            if all(grid_copy[row][col] != 0 for col in range(GRID_WIDTH)):
                del grid_copy[row]
                grid_copy.insert(0, [0 for _ in range(GRID_WIDTH)])
                lines_cleared += 1
            else:
                row -= 1
        
        return grid_copy, lines_cleared
    
    def check_collision_on_grid(self, piece, grid, dx=0, dy=0):
        """Check collision on a specific grid"""
        for block_x, block_y in piece.get_blocks():
            new_x = block_x + dx
            new_y = block_y + dy
            
            # Check boundaries
            if new_x < 0 or new_x >= GRID_WIDTH or new_y >= GRID_HEIGHT:
                return True
            
            # Check collision with placed blocks
            if new_y >= 0 and grid[new_y][new_x] != 0:
                return True
        
        return False
    
    def reset(self):
        """Reset the game state"""
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.grid_colors = [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.generator = TetrominoGenerator()
        self.current_piece = None
        self.next_pieces = []
        self.score = 0
        self.lines_cleared = 0
        self.level = 1
        self.fall_time = FALL_TIME
        self.last_fall = 0
        self.lock_delay_start = 0
        self.is_locking = False
        self.game_over = False
        self.spawn_new_piece()
