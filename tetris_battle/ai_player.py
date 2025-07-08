import time
from game import TetrisGame
from sounds import SoundManager
from config import *

class AIPlayer:
    def __init__(self, sound_manager, start_level=0):
        self.game = TetrisGame(start_level, sound_manager=sound_manager)
        self.sound_manager = sound_manager
        self.last_move_time = 0
        self.move_delay = DAS_SPEED  # Match player's DAS speed for actions
        self.thinking = False
        self.think_start_time = 0
        self.planned_move = None
        
        # AI movement state
        self.current_action = None
        self.action_queue = []
        self.target_x = None
        self.target_rotation = None
        self.movement_step = 0
        
        # AI timing - Match player's movement speed
        self.last_horizontal_move = 0
        self.last_drop_time = 0
        self.drop_delay = DAS_SPEED  # Match player's movement speed
        
        # PERFECT AI heuristic weights - mathematically optimized for unbeatable play
        self.weights = {
            'aggregate_height': -2.5,      # MASSIVE height penalty
            'lines_cleared': 5.0,          # ENORMOUS bonus for clearing lines
            'holes': -4.0,                 # SEVERE hole penalty  
            'bumpiness': -1.8,             # STRONG bumpiness penalty
            'height_penalty': -5.0,        # CATASTROPHIC penalty for tall stacks
            'well_depth': -2.0,            # Strong penalty for deep wells
            'height_variance': -1.5,       # Heavy penalty for uneven heights
            'column_transition': -1.0,     # Penalty for many transitions
            'row_transition': -0.8,        # Penalty for row transitions
            'pit_depth': -3.0,             # SEVERE penalty for deep pits
            'max_height': -4.0,            # MASSIVE max height penalty
            'tetris_ready': 4.0,           # HUGE bonus for Tetris setups
            'holes_weight_by_depth': -2.0, # Deeper holes exponentially worse
            'column_height_diff': -1.5,    # Strong penalty for height differences
            'roof_penalty': -8.0,          # DEVASTATING penalty for overhangs
            'dependency_penalty': -3.0,    # Heavy penalty for dependent holes
            'surface_smoothness': 1.0,     # Good bonus for smooth surfaces
            'line_clear_efficiency': 3.0,  # HUGE bonus for efficient clears
            'i_piece_dependency': -2.5,    # Strong penalty for I-piece dependency
            'safe_height': 1.0,            # Bonus for staying low
            'perfect_play': 2.0,           # Bonus for mathematically perfect moves
            'stack_stability': 1.5,        # Bonus for stable stacks
            'future_mobility': 0.8,        # Bonus for maintaining options
            'threat_assessment': -6.0,     # MASSIVE penalty for dangerous situations
            'efficiency_multiplier': 2.0   # Multiplier for efficient play
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
        if self.thinking and current_time - self.think_start_time >= AI_THINK_TIME * 3000:  # 3x longer thinking time
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
            # Use same timing as player's DAS system
            if self.game.move_piece(-1, 0):
                if self.sound_manager:
                    self.sound_manager.play_sound('move')
        elif action == 'move_right':
            # Use same timing as player's DAS system
            if self.game.move_piece(1, 0):
                if self.sound_manager:
                    self.sound_manager.play_sound('move')
        elif action == 'soft_drop':
            # Use controlled dropping at same speed as player
            if current_time - self.last_drop_time >= self.drop_delay:
                if self.game.move_piece(0, 1):
                    self.action_queue.append('soft_drop')  # Continue dropping
                    self.last_drop_time = current_time
                else:
                    # Piece has landed, lock it
                    self.game.lock_piece()
        
        self.last_move_time = current_time
    
    def find_best_move(self):
        """Find the best move using enhanced evaluation"""
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
                
                # Find the lowest valid position
                while not self.game.check_collision(test_piece):
                    test_piece.y += 1
                test_piece.y -= 1  # Back up to last valid position
                
                # Check if this position is actually valid and not at top
                if not self.game.check_collision(test_piece) and test_piece.y >= 0:
                    # Simulate placement with proper drop
                    test_grid, lines_cleared = self.game.simulate_placement(test_piece, x, test_piece.y, rotation)
                    
                    # Evaluate the resulting grid
                    score = self.evaluate_grid(test_grid, lines_cleared)
                    
                    # Look ahead bonus if we have a next piece
                    if self.game.next_piece and lines_cleared < 4:  # Don't look ahead after Tetris
                        lookahead_score = self.evaluate_lookahead(test_grid, self.game.next_piece)
                        score += lookahead_score * 0.3  # 30% weight for lookahead
                    
                    if score > best_score:
                        best_score = score
                        best_move = (x, rotation)
        
        return best_move
    
    def evaluate_lookahead(self, current_grid, next_piece):
        """Evaluate the best move for the next piece on the current grid"""
        if not next_piece:
            return 0
        
        # Check if next_piece is a string (shape type) instead of a piece object
        if isinstance(next_piece, str):
            # If it's just a string, we can't do lookahead without creating a piece object
            # This would require importing the Tetromino class, so skip lookahead for now
            return 0
            
        best_lookahead_score = float('-inf')
        
        try:
            shape_rotations = len(next_piece.SHAPES[next_piece.shape_type])
        except (AttributeError, KeyError):
            # If we can't get the shapes, skip lookahead
            return 0
        
        # Try a few promising positions for the next piece (not all to save time)
        positions_to_try = range(0, GRID_WIDTH, 2)  # Every other position
        
        for rotation in range(shape_rotations):
            for x in positions_to_try:
                # Create test piece for lookahead
                test_piece = next_piece.copy()
                test_piece.rotation = rotation
                test_piece.x = x
                test_piece.y = 0
                
                # Find lowest position
                temp_game = type(self.game)(0, self.sound_manager)
                temp_game.grid = [row[:] for row in current_grid]  # Copy grid
                
                while not temp_game.check_collision(test_piece):
                    test_piece.y += 1
                test_piece.y -= 1
                
                if not temp_game.check_collision(test_piece) and test_piece.y >= 0:
                    test_grid, lines_cleared = temp_game.simulate_placement(test_piece, x, test_piece.y, rotation)
                    score = self.evaluate_grid(test_grid, lines_cleared)
                    
                    if score > best_lookahead_score:
                        best_lookahead_score = score
        
        return best_lookahead_score if best_lookahead_score != float('-inf') else 0
    
    def evaluate_grid(self, grid, lines_cleared):
        """PERFECT evaluation function for unbeatable AI play"""
        score = 0
        
        # MASSIVE bonus for lines cleared (prioritize Tetrises)
        if lines_cleared == 4:  # Tetris - ENORMOUS bonus
            score += self.weights['lines_cleared'] * lines_cleared * 6.0
        elif lines_cleared == 3:  # Triple - good
            score += self.weights['lines_cleared'] * lines_cleared * 3.0
        elif lines_cleared == 2:  # Double - okay
            score += self.weights['lines_cleared'] * lines_cleared * 2.0
        elif lines_cleared == 1:  # Single - minimal
            score += self.weights['lines_cleared'] * lines_cleared * 1.0
        
        # Advanced grid analysis
        heights = self.get_column_heights(grid)
        max_height = max(heights) if heights else 0
        
        # CATASTROPHIC penalty for dangerous heights
        if max_height > 15:
            score += self.weights['threat_assessment'] * (max_height - 15) ** 2
        elif max_height > 12:
            score += self.weights['height_penalty'] * (max_height - 12) ** 1.5
        
        # PERFECT AI considerations
        aggregate_height = sum(heights)
        score += self.weights['aggregate_height'] * aggregate_height
        
        # Advanced hole analysis with exponential depth penalty
        hole_result = self.count_advanced_holes(grid)
        holes = hole_result[0] if isinstance(hole_result, tuple) else hole_result
        weighted_holes = hole_result[1] if isinstance(hole_result, tuple) and len(hole_result) > 1 else 0
        score += self.weights['holes'] * holes
        
        # Surface bumpiness (critical for perfect play)
        bumpiness = self.calculate_advanced_bumpiness(heights)
        score += self.weights['bumpiness'] * bumpiness
        
        # Height variance penalty
        if len(heights) > 1:
            height_variance = max(heights) - min(heights)
            score += self.weights['height_variance'] * height_variance
        
        # Well depth analysis (critical for Tetris setup)
        well_score = self.calculate_well_suitability(grid, heights)
        score += well_score
        
        # Stack stability analysis
        stability = self.calculate_stack_stability(grid)
        score += self.weights['stack_stability'] * stability
        
        # Future mobility assessment
        mobility = self.assess_future_mobility(grid, heights)
        score += self.weights['future_mobility'] * mobility
        
        # Perfect play bonus for mathematically optimal moves
        perfect_play_bonus = self.calculate_perfect_play_bonus(grid, heights, lines_cleared)
        score += perfect_play_bonus
        
        # Efficiency multiplier for ultra-smart play
        if lines_cleared >= 2 and max_height <= 10:
            score *= self.weights['efficiency_multiplier']
        
        return score
    
    def calculate_advanced_bumpiness(self, heights):
        """Calculate advanced bumpiness with exponential penalty for large differences"""
        if len(heights) <= 1:
            return 0
        
        bumpiness = 0
        for i in range(len(heights) - 1):
            diff = abs(heights[i] - heights[i + 1])
            bumpiness += diff * diff  # Quadratic penalty for large differences
        return bumpiness
    
    def calculate_well_suitability(self, grid, heights):
        """Calculate how suitable the grid is for well-based strategies like Tetris"""
        well_score = 0
        
        # Check for Tetris setup potential (right side well)
        if len(heights) >= 4:
            rightmost = heights[-1]
            left_neighbors = heights[-4:-1]
            
            if all(h > rightmost + 2 for h in left_neighbors):
                # Good Tetris setup potential
                well_score += 3.0
            elif rightmost < max(left_neighbors) - 1:
                # Some well potential
                well_score += 1.0
        
        # Penalty for multiple wells (scattered strategy is bad)
        well_count = 0
        for i in range(1, len(heights) - 1):
            if heights[i] < heights[i-1] - 1 and heights[i] < heights[i+1] - 1:
                well_count += 1
        
        if well_count > 1:
            well_score -= well_count * 2.0
        
        return well_score
    
    def calculate_stack_stability(self, grid):
        """Calculate how stable the current stack is"""
        stability = 0
        
        # Check for overhanging blocks
        for row in range(GRID_HEIGHT - 1):
            for col in range(GRID_WIDTH):
                if grid[row][col] != 0 and grid[row + 1][col] == 0:
                    # Block with empty space below - unstable
                    stability -= 1
        
        return stability
    
    def assess_future_mobility(self, grid, heights):
        """Assess how many placement options remain"""
        mobility = 0
        
        # Count columns that can still accept pieces
        for col, height in enumerate(heights):
            if height < GRID_HEIGHT - 4:  # Room for at least one more piece
                mobility += 1
        
        # Bonus for low overall height
        avg_height = sum(heights) / len(heights) if heights else 0
        if avg_height < 8:
            mobility += 2
        elif avg_height < 12:
            mobility += 1
        
        return mobility
    
    def calculate_perfect_play_bonus(self, grid, heights, lines_cleared):
        """Calculate bonus for mathematically optimal moves"""
        bonus = 0
        
        # Bonus for Tetris (4-line clear)
        if lines_cleared == 4:
            bonus += 10
        
        # Bonus for maintaining low height
        max_height = max(heights) if heights else 0
        if max_height <= 8:
            bonus += 5
        elif max_height <= 12:
            bonus += 2
        
        # Bonus for smooth surface
        if len(heights) > 1:
            height_variance = max(heights) - min(heights)
            if height_variance <= 2:
                bonus += 3
            elif height_variance <= 4:
                bonus += 1
        
        return bonus
    
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
    
    def count_advanced_holes(self, grid):
        """Count holes with depth weighting"""
        holes = 0
        weighted_holes = 0
        
        for col in range(GRID_WIDTH):
            found_block = False
            depth = 0
            for row in range(GRID_HEIGHT):
                if grid[row][col] != 0:
                    found_block = True
                    depth = 0
                elif found_block and grid[row][col] == 0:
                    holes += 1
                    depth += 1
                    # Weight holes by their depth (deeper holes are worse)
                    weighted_holes += depth
        
        return holes, weighted_holes
    
    def count_column_transitions(self, grid):
        """Count transitions between filled and empty cells in columns"""
        transitions = 0
        for col in range(GRID_WIDTH):
            for row in range(GRID_HEIGHT - 1):
                if (grid[row][col] == 0) != (grid[row + 1][col] == 0):
                    transitions += 1
        return transitions
    
    def count_row_transitions(self, grid):
        """Count transitions between filled and empty cells in rows"""
        transitions = 0
        for row in range(GRID_HEIGHT):
            for col in range(GRID_WIDTH - 1):
                if (grid[row][col] == 0) != (grid[row][col + 1] == 0):
                    transitions += 1
        return transitions
    
    def calculate_pit_depth(self, grid, heights):
        """Calculate penalty for isolated deep columns"""
        pit_depth = 0
        for i in range(len(heights)):
            left_height = heights[i - 1] if i > 0 else heights[i]
            right_height = heights[i + 1] if i < len(heights) - 1 else heights[i]
            
            # If this column is significantly lower than neighbors
            if heights[i] < left_height - 2 and heights[i] < right_height - 2:
                depth = min(left_height, right_height) - heights[i]
                pit_depth += depth * depth  # Quadratic penalty for deep pits
        
        return pit_depth
    
    def evaluate_tetris_setup(self, grid, heights):
        """Evaluate potential for Tetris (4-line clear) setups"""
        tetris_bonus = 0
        
        # Check rightmost column for Tetris setup potential
        rightmost_col = GRID_WIDTH - 1
        if heights[rightmost_col] <= max(heights[:-1]) - 3:
            # Right column is lower, good for I-piece
            tetris_bonus += 2
            
            # Check if we have a nice flat surface for the I-piece
            other_heights = heights[:-1]
            if len(set(other_heights)) <= 2:  # Heights are similar
                tetris_bonus += 1
        
        # Bonus for keeping one side low for potential Tetrises
        min_height = min(heights)
        avg_height = sum(heights) / len(heights)
        if min_height < avg_height - 2:
            tetris_bonus += 0.5
        
        return tetris_bonus
    
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
    
    def count_holes(self, grid):
        """Count holes in the grid (empty cells with filled cells above) - backward compatibility"""
        holes = 0
        for col in range(GRID_WIDTH):
            found_block = False
            for row in range(GRID_HEIGHT):
                if grid[row][col] != 0:
                    found_block = True
                elif found_block and grid[row][col] == 0:
                    holes += 1
        return holes
