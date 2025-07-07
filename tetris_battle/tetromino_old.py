import random
from config import COLORS

class Tetromino:
    # Tetromino shapes defined as rotation states
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
        """Get current shape matrix based on rotation"""
        return self.SHAPES[self.shape_type][self.rotation]
    
    def get_rotated_shape(self, rotation_offset=1):
        """Get shape matrix for a different rotation"""
        rotations = len(self.SHAPES[self.shape_type])
        new_rotation = (self.rotation + rotation_offset) % rotations
        return self.SHAPES[self.shape_type][new_rotation]
    
    def rotate(self):
        """Rotate the tetromino clockwise"""
        rotations = len(self.SHAPES[self.shape_type])
        self.rotation = (self.rotation + 1) % rotations
    
    def get_blocks(self):
        """Get list of absolute block positions"""
        blocks = []
        shape = self.get_shape()
        for row in range(len(shape)):
            for col in range(len(shape[row])):
                if shape[row][col]:
                    blocks.append((self.x + col, self.y + row))
        return blocks
    
    def get_rotated_blocks(self, rotation_offset=1):
        """Get blocks for a rotated version without actually rotating"""
        blocks = []
        shape = self.get_rotated_shape(rotation_offset)
        for row in range(len(shape)):
            for col in range(len(shape[row])):
                if shape[row][col]:
                    blocks.append((self.x + col, self.y + row))
        return blocks
    
    def copy(self):
        """Create a copy of this tetromino"""
        new_piece = Tetromino(self.shape_type, self.x, self.y)
        new_piece.rotation = self.rotation
        return new_piece

class TetrominoGenerator:
    """Generates tetrominoes using the 7-bag system"""
    
    def __init__(self):
        self.bag = []
        self.refill_bag()
    
    def refill_bag(self):
        """Refill the bag with one of each tetromino type"""
        shapes = list(Tetromino.SHAPES.keys())
        random.shuffle(shapes)
        self.bag.extend(shapes)
    
    def get_next(self):
        """Get the next tetromino from the bag"""
        if not self.bag:
            self.refill_bag()
        
        shape_type = self.bag.pop(0)
        return Tetromino(shape_type)
    
    def peek(self, count=1):
        """Peek at the next few pieces without removing them"""
        # Make sure we have enough pieces
        while len(self.bag) < count:
            self.refill_bag()
        
        return [Tetromino(shape_type) for shape_type in self.bag[:count]]
