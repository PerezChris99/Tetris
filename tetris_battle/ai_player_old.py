import time
import random
from game import TetrisGame
from sounds import SoundManager
from config import AI_THINK_TIME, GRID_WIDTH, GRID_HEIGHT

class AIPlayer:
    def __init__(self, sound_manager):
        self.game = TetrisGame()
        self.sound_manager = sound_manager
        self.last_move_time = 0
        self.move_delay = 500  # ms between moves
        self.thinking = False
        self.think_start_time = 0
        self.planned_move = None
        
        # AI heuristic weights (tuned for good performance)
        self.weights = {
            'aggregate_height': -0.510066,
            'lines_cleared': 0.760666,
            'holes': -0.35663,
            'bumpiness': -0.184483,
            'height_penalty': -0.1,
            'well_depth': -0.05
        }
    
    def update(self, dt):
        """Update AI state"""
        if self.game.game_over:
            return
        
        current_time = time.time() * 1000  # Convert to ms
        
        # Update game state
        self.game.update(dt)
        
        # Check if it's time to make a move
        if current_time - self.last_move_time >= self.move_delay:
            if not self.thinking and self.game.current_piece:
                self.start_thinking()
            elif self.thinking and current_time - self.think_start_time >= AI_THINK_TIME * 1000:
                self.execute_planned_move()
    
    def start_thinking(self):
        """Start thinking about the next move"""
        self.thinking = True
        self.think_start_time = time.time() * 1000
        self.planned_move = self.find_best_move()
    
    def execute_planned_move(self):
        """Execute the planned move"""
        if self.planned_move:
            target_x, target_rotation = self.planned_move
            
            # Rotate to target rotation
            current_rotation = self.game.current_piece.rotation
            rotations_needed = (target_rotation - current_rotation) % len(self.game.current_piece.SHAPES[self.game.current_piece.shape_type])
            
            for _ in range(rotations_needed):
                if self.game.rotate_piece():
                    self.sound_manager.play_sound('rotate')
            
            # Move to target x position
            current_x = self.game.current_piece.x
            if target_x < current_x:
                for _ in range(current_x - target_x):
                    if not self.game.move_piece(-1, 0):
                        break
                    self.sound_manager.play_sound('move')
            elif target_x > current_x:
                for _ in range(target_x - current_x):
                    if not self.game.move_piece(1, 0):
                        break
                    self.sound_manager.play_sound('move')
            
            # Hard drop
            drop_distance = self.game.hard_drop()
            if drop_distance > 0:
                self.sound_manager.play_sound('drop')
        
        self.thinking = False
        self.planned_move = None
        self.last_move_time = time.time() * 1000
    
    def find_best_move(self):
        """Find the best move for the current piece"""
        if not self.game.current_piece:
            return None
        
        best_score = float('-inf')
        best_move = None
        
        piece = self.game.current_piece
        shape_rotations = len(piece.SHAPES[piece.shape_type])
        
        # Try all possible rotations and positions
        for rotation in range(shape_rotations):
            for x in range(GRID_WIDTH):
                # Create a test piece at this position and rotation
                test_piece = piece.copy()
                test_piece.x = x
                test_piece.rotation = rotation
                
                # Check if this position is valid
                if self.game.check_collision(test_piece):
                    continue
                
                # Simulate the placement
                try:
                    grid_result, lines_cleared = self.game.simulate_placement(piece, x, 0, rotation)
                    score = self.evaluate_grid(grid_result, lines_cleared)
                    
                    if score > best_score:
                        best_score = score
                        best_move = (x, rotation)
                except:
                    # Skip invalid moves
                    continue
        
        return best_move
    
    def evaluate_grid(self, grid, lines_cleared):
        """Evaluate a grid state using heuristics"""
        score = 0
        
        # Lines cleared bonus
        score += self.weights['lines_cleared'] * lines_cleared
        
        # Calculate aggregate height
        heights = self.get_column_heights(grid)
        aggregate_height = sum(heights)
        score += self.weights['aggregate_height'] * aggregate_height
        
        # Calculate bumpiness (difference in adjacent column heights)
        bumpiness = 0
        for i in range(len(heights) - 1):
            bumpiness += abs(heights[i] - heights[i + 1])
        score += self.weights['bumpiness'] * bumpiness
        
        # Calculate holes
        holes = self.count_holes(grid)
        score += self.weights['holes'] * holes
        
        # Height penalty for very tall stacks
        max_height = max(heights) if heights else 0
        if max_height > 15:
            score += self.weights['height_penalty'] * (max_height - 15) ** 2
        
        # Well depth penalty
        well_depth = self.calculate_well_depth(grid, heights)
        score += self.weights['well_depth'] * well_depth
        
        return score
    
    def get_column_heights(self, grid):
        """Get the height of each column"""
        heights = []
        for col in range(GRID_WIDTH):
            height = 0
            for row in range(GRID_HEIGHT):
                if grid[row][col] != 0:
                    height = GRID_HEIGHT - row
                    break
            heights.append(height)
        return heights
    
    def count_holes(self, grid):
        """Count holes in the grid (empty cells with filled cells above)"""
        holes = 0
        for col in range(GRID_WIDTH):
            block_found = False
            for row in range(GRID_HEIGHT):
                if grid[row][col] != 0:
                    block_found = True
                elif block_found and grid[row][col] == 0:
                    holes += 1
        return holes
    
    def calculate_well_depth(self, grid, heights):
        """Calculate depth of wells (deep columns surrounded by taller columns)"""
        well_depth = 0
        for i in range(len(heights)):
            left_height = heights[i - 1] if i > 0 else 0
            right_height = heights[i + 1] if i < len(heights) - 1 else 0
            current_height = heights[i]
            
            # Check if this is a well (both neighbors are taller)
            if left_height > current_height and right_height > current_height:
                well_depth += min(left_height, right_height) - current_height
        
        return well_depth
    
    def reset(self):
        """Reset AI state"""
        self.game.reset()
        self.thinking = False
        self.planned_move = None
        self.last_move_time = 0
