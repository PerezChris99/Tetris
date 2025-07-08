import random
from config import COLORS

class Tetromino:
    # Game Boy Tetris rotation system - left-handed Nintendo rotation (no wall kicks)
    SHAPES = {
        'I': [
            [[0, 0, 0, 0],
             [1, 1, 1, 1],
             [0, 0, 0, 0],
             [0, 0, 0, 0]],
            [[0, 0, 1, 0],
             [0, 0, 1, 0],
             [0, 0, 1, 0],
             [0, 0, 1, 0]],
            [[0, 0, 0, 0],
             [0, 0, 0, 0],
             [1, 1, 1, 1],
             [0, 0, 0, 0]],
            [[0, 1, 0, 0],
             [0, 1, 0, 0],
             [0, 1, 0, 0],
             [0, 1, 0, 0]]
        ],
        'O': [
            [[0, 1, 1, 0],
             [0, 1, 1, 0],
             [0, 0, 0, 0],
             [0, 0, 0, 0]]
        ],
        'T': [
            [[0, 1, 0, 0],
             [1, 1, 1, 0],
             [0, 0, 0, 0],
             [0, 0, 0, 0]],
            [[0, 1, 0, 0],
             [0, 1, 1, 0],
             [0, 1, 0, 0],
             [0, 0, 0, 0]],
            [[0, 0, 0, 0],
             [1, 1, 1, 0],
             [0, 1, 0, 0],
             [0, 0, 0, 0]],
            [[0, 1, 0, 0],
             [1, 1, 0, 0],
             [0, 1, 0, 0],
             [0, 0, 0, 0]]
        ],
        'S': [
            [[0, 1, 1, 0],
             [1, 1, 0, 0],
             [0, 0, 0, 0],
             [0, 0, 0, 0]],
            [[0, 1, 0, 0],
             [0, 1, 1, 0],
             [0, 0, 1, 0],
             [0, 0, 0, 0]],
            [[0, 0, 0, 0],
             [0, 1, 1, 0],
             [1, 1, 0, 0],
             [0, 0, 0, 0]],
            [[1, 0, 0, 0],
             [1, 1, 0, 0],
             [0, 1, 0, 0],
             [0, 0, 0, 0]]
        ],
        'Z': [
            [[1, 1, 0, 0],
             [0, 1, 1, 0],
             [0, 0, 0, 0],
             [0, 0, 0, 0]],
            [[0, 0, 1, 0],
             [0, 1, 1, 0],
             [0, 1, 0, 0],
             [0, 0, 0, 0]],
            [[0, 0, 0, 0],
             [1, 1, 0, 0],
             [0, 1, 1, 0],
             [0, 0, 0, 0]],
            [[0, 1, 0, 0],
             [1, 1, 0, 0],
             [1, 0, 0, 0],
             [0, 0, 0, 0]]
        ],
        'J': [
            [[1, 0, 0, 0],
             [1, 1, 1, 0],
             [0, 0, 0, 0],
             [0, 0, 0, 0]],
            [[0, 1, 1, 0],
             [0, 1, 0, 0],
             [0, 1, 0, 0],
             [0, 0, 0, 0]],
            [[0, 0, 0, 0],
             [1, 1, 1, 0],
             [0, 0, 1, 0],
             [0, 0, 0, 0]],
            [[0, 1, 0, 0],
             [0, 1, 0, 0],
             [1, 1, 0, 0],
             [0, 0, 0, 0]]
        ],
        'L': [
            [[0, 0, 1, 0],
             [1, 1, 1, 0],
             [0, 0, 0, 0],
             [0, 0, 0, 0]],
            [[0, 1, 0, 0],
             [0, 1, 0, 0],
             [0, 1, 1, 0],
             [0, 0, 0, 0]],
            [[0, 0, 0, 0],
             [1, 1, 1, 0],
             [1, 0, 0, 0],
             [0, 0, 0, 0]],
            [[1, 1, 0, 0],
             [0, 1, 0, 0],
             [0, 1, 0, 0],
             [0, 0, 0, 0]]
        ]
    }
    
    def __init__(self, shape_type=None, x=3, y=0):
        if shape_type is None:
            self.shape_type = random.choice(list(self.SHAPES.keys()))
        else:
            self.shape_type = shape_type
        
        self.x = x
        self.y = y
        self.rotation = 0
        self.color = COLORS[self.shape_type]
        
    def get_shape(self):
        return self.SHAPES[self.shape_type][self.rotation]
    
    def get_rotated_shape(self, rotation_offset=1):
        rotations = len(self.SHAPES[self.shape_type])
        new_rotation = (self.rotation + rotation_offset) % rotations
        return self.SHAPES[self.shape_type][new_rotation]
    
    def rotate(self):
        """Rotate piece - Game Boy style, no wall kicks"""
        rotations = len(self.SHAPES[self.shape_type])
        self.rotation = (self.rotation + 1) % rotations
    
    def get_blocks(self):
        """Get list of block positions for current piece"""
        blocks = []
        shape = self.get_shape()
        for row in range(4):
            for col in range(4):
                if shape[row][col]:
                    blocks.append((self.x + col, self.y + row))
        return blocks
    
    def get_rotated_blocks(self, rotation_offset=1):
        """Get blocks for rotated piece without actually rotating"""
        blocks = []
        shape = self.get_rotated_shape(rotation_offset)
        for row in range(4):
            for col in range(4):
                if shape[row][col]:
                    blocks.append((self.x + col, self.y + row))
        return blocks
    
    def copy(self):
        """Create a copy of this tetromino"""
        new_piece = Tetromino(self.shape_type, self.x, self.y)
        new_piece.rotation = self.rotation
        return new_piece


class GameBoyRandomizer:
    """Game Boy Tetris pseudo-random piece generator
    
    Implements a simplified version that ensures good piece distribution
    while preventing the same piece from appearing too frequently.
    """
    
    def __init__(self):
        self.pieces = ['I', 'O', 'T', 'S', 'Z', 'J', 'L']
        self.bag = self.pieces.copy()
        self.current_piece = None
        self.next_piece = None
        self._generate_initial_pieces()
    
    def _generate_initial_pieces(self):
        """Generate first two pieces"""
        self.current_piece = random.choice(self.pieces)
        self.next_piece = self._get_random_piece()
    
    def _get_random_piece(self):
        """Get a random piece using bag randomizer for better distribution"""
        if not self.bag:
            # Refill the bag with all pieces
            self.bag = self.pieces.copy()
            # Shuffle to ensure randomness
            random.shuffle(self.bag)
        
        # Remove and return a piece from the bag
        return self.bag.pop()
    
    def get_next(self):
        """Get the next piece"""
        piece = Tetromino(self.current_piece)
        
        # Move pieces forward
        self.current_piece = self.next_piece
        self.next_piece = self._get_random_piece()
        
        return piece
    
    def peek(self, count=1):
        """Peek at upcoming pieces (Game Boy only shows 1 next piece)"""
        if count == 1:
            return [Tetromino(self.current_piece)]
        else:
            # Game Boy only shows 1 next piece
            return [Tetromino(self.current_piece)]


# Alias for backwards compatibility
TetrominoGenerator = GameBoyRandomizer
