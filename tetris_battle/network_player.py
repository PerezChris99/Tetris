"""
Network Player class for online multiplayer Tetris
Handles remote player input and synchronization
"""
import pygame
import time
from typing import Optional, Dict, Any
from game import TetrisGame
from sounds import SoundManager
from config import *
from network_protocol import NetworkMessage, MessageType

class NetworkPlayer:
    """Represents a remote player in online multiplayer"""
    
    def __init__(self, player_id: str, sound_manager: SoundManager, start_level: int = 0, is_local: bool = True):
        self.player_id = player_id
        self.game = TetrisGame(start_level, sound_manager=sound_manager)
        self.sound_manager = sound_manager
        self.is_local = is_local
        self.start_level = start_level
        
        # Input state for local player
        if is_local:
            self.keys_pressed = set()
            self.last_move_time = 0
            self.last_soft_drop_time = 0
            self.das_timer = 0
            self.das_active = False
            self.das_direction = 0
            self.soft_drop_active = False
        
        # Network synchronization
        self.last_state_update = 0
        self.state_update_interval = 100  # ms between state updates
        self.network_manager = None
        
        # Game state tracking for network sync
        self.last_sent_state = None
        self.pending_inputs = []
        
    def set_network_manager(self, network_manager):
        """Set the network manager for sending messages"""
        self.network_manager = network_manager
        
        if network_manager:
            # Register message handlers
            network_manager.register_handler(MessageType.PLAYER_INPUT, self._handle_remote_input)
            network_manager.register_handler(MessageType.GAME_STATE, self._handle_game_state)
            network_manager.register_handler(MessageType.PIECE_DROP, self._handle_piece_drop)
            network_manager.register_handler(MessageType.LINE_CLEAR, self._handle_line_clear)
            network_manager.register_handler(MessageType.GARBAGE_SEND, self._handle_garbage_receive)
    
    def handle_input(self, keys):
        """Handle player input (local player only)"""
        if not self.is_local or self.game.game_over or self.game.clear_animation_active:
            return
        
        current_time = time.time() * 1000  # Convert to milliseconds
        input_data = {}
        
        # Handle rotation (A button)
        if keys[pygame.K_UP] and pygame.K_UP not in self.keys_pressed:
            if self.game.rotate_piece():
                self.sound_manager.play_sound('rotate')
                input_data['action'] = 'rotate'
                input_data['success'] = True
        
        # Handle hard drop (spacebar)
        if keys[pygame.K_SPACE] and pygame.K_SPACE not in self.keys_pressed:
            self.hard_drop()
            input_data['action'] = 'hard_drop'
        
        # Handle horizontal movement with DAS
        left_pressed = keys[pygame.K_LEFT]
        right_pressed = keys[pygame.K_RIGHT]
        
        if left_pressed and not right_pressed:
            moved = self._handle_horizontal_movement(-1, current_time)
            if moved:
                input_data['action'] = 'move'
                input_data['direction'] = 'left'
        elif right_pressed and not left_pressed:
            moved = self._handle_horizontal_movement(1, current_time)
            if moved:
                input_data['action'] = 'move'
                input_data['direction'] = 'right'
        else:
            self.das_active = False
            self.das_timer = 0
            self.das_direction = 0
        
        # Handle soft drop
        if keys[pygame.K_DOWN]:
            if not self.soft_drop_active:
                self.soft_drop_active = True
                self.last_soft_drop_time = current_time
                if self.game.soft_drop() > 0:
                    self.sound_manager.play_sound('move')
                    input_data['action'] = 'soft_drop'
            else:
                # Continuous soft drop
                current_gravity = frames_to_ms(GRAVITY_TABLE[min(self.game.level, MAX_LEVEL)])
                soft_drop_speed = current_gravity / SOFT_DROP_MULTIPLIER
                
                if current_time - self.last_soft_drop_time >= soft_drop_speed:
                    if self.game.soft_drop() > 0:
                        self.sound_manager.play_sound('move')
                        input_data['action'] = 'soft_drop'
                    self.last_soft_drop_time = current_time
        else:
            self.soft_drop_active = False
        
        # Send input data to remote player if any action occurred
        if input_data and self.network_manager:
            self._send_input(input_data)
        
        # Update pressed keys
        self.keys_pressed = {key for key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_DOWN, pygame.K_UP, pygame.K_SPACE] if keys[key]}
    
    def _handle_horizontal_movement(self, direction: int, current_time: float) -> bool:
        """Handle horizontal movement with DAS"""
        moved = False
        
        if self.das_direction != direction:
            # Direction changed or first press
            self.das_direction = direction
            self.das_active = False
            self.das_timer = current_time
            
            # Immediate move on first press
            if self.game.move_piece(direction, 0):
                self.sound_manager.play_sound('move')
                moved = True
        else:
            # Same direction held
            if not self.das_active:
                # Check if DAS delay has passed
                if current_time - self.das_timer >= DAS_DELAY:
                    self.das_active = True
                    self.das_timer = current_time
            else:
                # DAS is active, check for repeat
                if current_time - self.das_timer >= DAS_SPEED:
                    if self.game.move_piece(direction, 0):
                        self.sound_manager.play_sound('move')
                        moved = True
                    self.das_timer = current_time
        
        return moved
    
    def hard_drop(self):
        """Perform hard drop"""
        if not self.game.current_piece or self.game.game_over:
            return
        
        drop_distance = 0
        while not self.game.check_collision(self.game.current_piece, 0, 1):
            self.game.current_piece.y += 1
            drop_distance += 1
        
        # Award points for hard drop distance
        self.game.score = min(self.game.score + drop_distance * 2, MAX_SCORE)
        
        # Lock the piece immediately
        self.game.lock_piece()
        
        # Play drop sound
        self.sound_manager.play_sound('drop')
    
    def update(self, dt: float):
        """Update player state"""
        self.game.update(dt)
        
        # Send periodic state updates for local player
        if self.is_local and self.network_manager:
            current_time = time.time() * 1000
            if current_time - self.last_state_update >= self.state_update_interval:
                self._send_game_state()
                self.last_state_update = current_time
    
    def reset(self):
        """Reset player state"""
        self.game.reset()
        
        if self.is_local:
            self.keys_pressed = set()
            self.das_active = False
            self.das_direction = 0
            self.das_timer = 0
            self.soft_drop_active = False
        
        self.last_state_update = 0
        self.last_sent_state = None
        self.pending_inputs = []
    
    def _send_input(self, input_data: Dict[str, Any]):
        """Send input action to remote player"""
        if not self.network_manager:
            return
        
        message = NetworkMessage(MessageType.PLAYER_INPUT, {
            'input': input_data,
            'timestamp': time.time() * 1000,
            'game_time': time.time()  # For synchronization
        })
        
        self.network_manager.send_message(message)
    
    def _send_game_state(self):
        """Send current game state to remote player"""
        if not self.network_manager:
            return
        
        # Create state snapshot
        state = {
            'grid': self.game.grid,
            'score': self.game.score,
            'lines_cleared': self.game.lines_cleared,
            'pieces_dropped': self.game.pieces_dropped,
            'level': self.game.level,
            'game_over': self.game.game_over,
            'current_piece': None,
            'next_piece': self.game.next_piece,
            'clearing_lines': self.game.clearing_lines,
            'clear_animation_active': self.game.clear_animation_active,
            'timestamp': time.time() * 1000
        }
        
        # Include current piece data
        if self.game.current_piece:
            state['current_piece'] = {
                'type': self.game.current_piece.type,
                'x': self.game.current_piece.x,
                'y': self.game.current_piece.y,
                'rotation': self.game.current_piece.rotation
            }
        
        # Only send if state has changed significantly
        if self._state_changed(state):
            message = NetworkMessage(MessageType.GAME_STATE, state)
            self.network_manager.send_message(message)
            self.last_sent_state = state.copy()
    
    def _state_changed(self, current_state: Dict[str, Any]) -> bool:
        """Check if game state has changed significantly"""
        if not self.last_sent_state:
            return True
        
        # Check critical state changes
        critical_fields = ['score', 'lines_cleared', 'level', 'game_over', 'current_piece', 'clearing_lines']
        
        for field in critical_fields:
            if current_state.get(field) != self.last_sent_state.get(field):
                return True
        
        # Check grid changes (only compare a few key rows for performance)
        current_grid = current_state.get('grid', [])
        last_grid = self.last_sent_state.get('grid', [])
        
        if len(current_grid) != len(last_grid):
            return True
        
        # Compare bottom 5 rows (most likely to change)
        for i in range(max(0, len(current_grid) - 5), len(current_grid)):
            if current_grid[i] != last_grid[i]:
                return True
        
        return False
    
    def _handle_remote_input(self, message: NetworkMessage):
        """Handle input from remote player"""
        if self.is_local:  # Only remote players should handle this
            return
        
        input_data = message.data.get('input', {})
        action = input_data.get('action')
        
        if not action:
            return
        
        # Apply remote input to our game state
        if action == 'move':
            direction = 1 if input_data.get('direction') == 'right' else -1
            self.game.move_piece(direction, 0)
        elif action == 'rotate':
            if input_data.get('success', False):
                self.game.rotate_piece()
        elif action == 'soft_drop':
            self.game.soft_drop()
        elif action == 'hard_drop':
            self.hard_drop()
    
    def _handle_game_state(self, message: NetworkMessage):
        """Handle game state update from remote player"""
        if self.is_local:  # Only remote players should handle this
            return
        
        state = message.data
        
        # Update non-critical state
        self.game.score = state.get('score', 0)
        self.game.lines_cleared = state.get('lines_cleared', 0)
        self.game.pieces_dropped = state.get('pieces_dropped', 0)
        self.game.level = state.get('level', 0)
        self.game.game_over = state.get('game_over', False)
        self.game.next_piece = state.get('next_piece')
        self.game.clearing_lines = state.get('clearing_lines', [])
        self.game.clear_animation_active = state.get('clear_animation_active', False)
        
        # Update grid state
        if 'grid' in state:
            self.game.grid = state['grid']
        
        # Update current piece
        piece_data = state.get('current_piece')
        if piece_data:
            from tetromino import Tetromino
            self.game.current_piece = Tetromino(piece_data['type'])
            self.game.current_piece.x = piece_data['x']
            self.game.current_piece.y = piece_data['y']
            self.game.current_piece.rotation = piece_data['rotation']
        else:
            self.game.current_piece = None
    
    def _handle_piece_drop(self, message: NetworkMessage):
        """Handle piece drop notification"""
        if not self.is_local:
            return
        
        # Remote player dropped a piece, we might need to sync
        pass
    
    def _handle_line_clear(self, message: NetworkMessage):
        """Handle line clear notification"""
        if not self.is_local:
            return
        
        # Remote player cleared lines, play appropriate sound
        lines_cleared = message.data.get('lines', 0)
        if lines_cleared > 0:
            self.sound_manager.play_sound('clear')
    
    def _handle_garbage_receive(self, message: NetworkMessage):
        """Handle receiving garbage lines from opponent"""
        garbage_lines = message.data.get('lines', 0)
        if garbage_lines > 0:
            self.game.receive_garbage_lines(garbage_lines)
            print(f"Received {garbage_lines} garbage lines from opponent")
    
    def send_garbage_to_opponent(self, lines_cleared: int):
        """Send garbage lines to opponent"""
        if not self.network_manager or not self.is_local:
            return
        
        garbage_to_send = self.game.send_garbage_lines(lines_cleared)
        if garbage_to_send > 0:
            message = NetworkMessage(MessageType.GARBAGE_SEND, {
                'lines': garbage_to_send,
                'from_lines': lines_cleared
            })
            self.network_manager.send_message(message)
            print(f"Sent {garbage_to_send} garbage lines to opponent")
