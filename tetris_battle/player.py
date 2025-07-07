import pygame
from game import TetrisGame
from sounds import SoundManager

class Player:
    def __init__(self, sound_manager):
        self.game = TetrisGame()
        self.sound_manager = sound_manager
        self.keys_pressed = set()
        self.last_move_time = 0
        self.last_soft_drop_time = 0
        self.move_repeat_delay = 150  # ms
        self.soft_drop_repeat_delay = 50  # ms
        self.das_delay = 250  # Delayed Auto Shift initial delay
        self.das_speed = 50   # Delayed Auto Shift repeat speed
        self.das_timer = 0
        self.das_active = False
        self.das_direction = 0
    
    def handle_input(self, keys):
        """Handle player input"""
        if self.game.game_over:
            return
        
        current_time = pygame.time.get_ticks()
        
        # Handle rotation
        if keys[pygame.K_UP] and pygame.K_UP not in self.keys_pressed:
            if self.game.rotate_piece():
                self.sound_manager.play_sound('rotate')
        
        # Handle hard drop
        if keys[pygame.K_SPACE] and pygame.K_SPACE not in self.keys_pressed:
            drop_distance = self.game.hard_drop()
            if drop_distance > 0:
                self.sound_manager.play_sound('drop')
        
        # Handle horizontal movement with DAS (Delayed Auto Shift)
        left_pressed = keys[pygame.K_LEFT]
        right_pressed = keys[pygame.K_RIGHT]
        
        if left_pressed and not right_pressed:
            self._handle_horizontal_movement(-1, current_time)
        elif right_pressed and not left_pressed:
            self._handle_horizontal_movement(1, current_time)
        else:
            self.das_active = False
            self.das_timer = 0
            self.das_direction = 0
        
        # Handle soft drop
        if keys[pygame.K_DOWN]:
            if pygame.K_DOWN not in self.keys_pressed:
                # First press
                if self.game.move_piece(0, 1):
                    self.sound_manager.play_sound('move')
                self.last_soft_drop_time = current_time
            elif current_time - self.last_soft_drop_time >= self.soft_drop_repeat_delay:
                # Repeat soft drop
                if self.game.move_piece(0, 1):
                    self.sound_manager.play_sound('move')
                self.last_soft_drop_time = current_time
        
        # Update pressed keys
        self.keys_pressed = {key for key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_DOWN, pygame.K_UP, pygame.K_SPACE] if keys[key]}
    
    def _handle_horizontal_movement(self, direction, current_time):
        """Handle horizontal movement with DAS"""
        if self.das_direction != direction:
            # Direction changed or first press
            self.das_direction = direction
            self.das_active = False
            self.das_timer = current_time
            
            # Immediate move on first press
            if self.game.move_piece(direction, 0):
                self.sound_manager.play_sound('move')
        else:
            # Same direction held
            if not self.das_active:
                # Check if DAS delay has passed
                if current_time - self.das_timer >= self.das_delay:
                    self.das_active = True
                    self.das_timer = current_time
            else:
                # DAS is active, check for repeat
                if current_time - self.das_timer >= self.das_speed:
                    if self.game.move_piece(direction, 0):
                        self.sound_manager.play_sound('move')
                    self.das_timer = current_time
    
    def update(self, dt):
        """Update player state"""
        self.game.update(dt)
    
    def reset(self):
        """Reset player state"""
        self.game.reset()
        self.keys_pressed = set()
        self.das_active = False
        self.das_direction = 0
        self.das_timer = 0
