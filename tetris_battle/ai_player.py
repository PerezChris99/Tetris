import time
from game import TetrisGame
from sounds import SoundManager
from config import *

class AIPlayer:
    def __init__(self, sound_manager, start_level=0):
        self.game = TetrisGame(start_level, sound_manager=sound_manager)
        self.sound_manager = sound_manager
        self.last_move_time = 0
        self.move_delay = 200  # ms between moves (same as player DAS speed)
        self.thinking = False
        self.think_start_time = 0
        self.planned_move = None
        
        # AI movement state
        self.current_action = None
        self.action_queue = []
        self.target_x = None
        self.target_rotation = None
        self.movement_step = 0
        
        # AI timing to match player behavior
        self.last_horizontal_move = 0
        self.last_drop_time = 0
        self.drop_delay = 100  # ms between drops (similar to soft drop)
        
        # AI heuristic weights (tuned for Game Boy Tetris)
        self.weights = {
            'aggregate_height': -0.510066,
            'lines_cleared': 0.760666,
            'holes': -0.35663,
            'bumpiness': -0.184483,
            'height_penalty': -0.2,
            'well_depth': -0.1
        }
    
    def update(self, dt):
        """Update AI state"""
        if self.game.game_over:
            return
        
        current_time = time.time() * 1000  # Convert to ms
        
        # Update game state first
        self.game.update(dt)
        
        # If game over after update, stop
        if self.game.game_over:
            return
        
        # Don't move during line clearing animation
        if self.game.clear_animation_active:
            return
        
        # Check if we need to start thinking about a new piece
        if self.game.current_piece and not self.thinking and not self.action_queue:
            self.start_thinking()
        
        # Check if thinking time is up
        if self.thinking and current_time - self.think_start_time >= AI_THINK_TIME * 1000:
            self.plan_actions()
        
        # Execute actions if we have them
        if self.action_queue and current_time - self.last_move_time >= self.move_delay:
            self.execute_next_action()
        
        # Fallback: if no actions and piece exists, think again
        if not self.action_queue and not self.thinking and self.game.current_piece:
            self.start_thinking()
    
    def start_thinking(self):
        """Start thinking about the next move"""
        self.thinking = True
        self.think_start_time = time.time() * 1000
        self.planned_move = self.find_best_move()
    
    def plan_actions(self):
        """Plan the sequence of actions to reach the target"""
        if self.planned_move:
            target_x, target_rotation = self.planned_move
            current_piece = self.game.current_piece
            
            if current_piece:
                self.action_queue = []
                
                # Add rotation actions
                rotations_needed = (target_rotation - current_piece.rotation) % 4
                for _ in range(rotations_needed):
                    self.action_queue.append('rotate')
                
                # Add horizontal movement actions
                x_diff = target_x - current_piece.x
                if x_diff < 0:
                    for _ in range(abs(x_diff)):
                        self.action_queue.append('move_left')
                elif x_diff > 0:
                    for _ in range(x_diff):
                        self.action_queue.append('move_right')
                
                # Add soft drop actions (move down gradually)
                self.action_queue.append('soft_drop')
        
        self.thinking = False
        self.planned_move = None
    
    def execute_next_action(self):
        """Execute the next action in the queue"""
        if not self.action_queue:
            return
        
        current_piece = self.game.current_piece
        if not current_piece:
            self.action_queue = []
            return
        
        action = self.action_queue.pop(0)
        current_time = time.time() * 1000
        
        if action == 'rotate':
            if self.game.rotate_piece():
                if self.sound_manager:
                    self.sound_manager.play_sound('rotate')
        elif action == 'move_left':
            if current_time - self.last_horizontal_move >= DAS_SPEED:
                if self.game.move_piece(-1, 0):
                    if self.sound_manager:
                        self.sound_manager.play_sound('move')
                self.last_horizontal_move = current_time
        elif action == 'move_right':
            if current_time - self.last_horizontal_move >= DAS_SPEED:
                if self.game.move_piece(1, 0):
                    if self.sound_manager:
                        self.sound_manager.play_sound('move')
                self.last_horizontal_move = current_time
        elif action == 'soft_drop':
            # Use controlled dropping like the player
            if current_time - self.last_drop_time >= self.drop_delay:
                if self.game.move_piece(0, 1):
                    self.action_queue.append('soft_drop')  # Continue dropping
                    self.last_drop_time = current_time
                else:
                    # Piece has landed, lock it
                    self.game.lock_piece()
        
        self.last_move_time = current_time
    
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
                # Create test piece
                test_piece = piece.copy()
                test_piece.rotation = rotation
                test_piece.x = x
                test_piece.y = 0
                
                # Check if this position is valid
                if not self.game.check_collision(test_piece):
                    # Simulate placement
                    test_grid, lines_cleared = self.game.simulate_placement(test_piece, x, 0, rotation)
                    
                    # Evaluate the resulting grid
                    score = self.evaluate_grid(test_grid, lines_cleared)
                    
                    if score > best_score:
                        best_score = score
                        best_move = (x, rotation)
        
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
            score += self.weights['height_penalty'] * (max_height - 15)
        
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
            found_block = False
            for row in range(GRID_HEIGHT):
                if grid[row][col] != 0:
                    found_block = True
                elif found_block and grid[row][col] == 0:
                    holes += 1
        return holes
    
    def calculate_well_depth(self, grid, heights):
        """Calculate depth of wells (deep columns surrounded by taller columns)"""
        well_depth = 0
        for i in range(len(heights)):
            left_height = heights[i - 1] if i > 0 else 0
            right_height = heights[i + 1] if i < len(heights) - 1 else 0
            
            if heights[i] < left_height and heights[i] < right_height:
                well_depth += min(left_height, right_height) - heights[i]
        
        return well_depth
    
    def reset(self):
        """Reset AI state"""
        self.game.reset()
        self.thinking = False
        self.planned_move = None
        self.last_move_time = 0
        self.action_queue = []
        self.current_action = None
        self.target_x = None
        self.target_rotation = None
        self.movement_step = 0
        self.last_horizontal_move = 0
        self.last_drop_time = 0
