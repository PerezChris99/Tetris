import pygame
import time
from game import TetrisGame
from sounds import SoundManager
from config import *

class Player:
    def __init__(self, sound_manager, start_level=0):
        self.game = TetrisGame(start_level)
        self.sound_manager = sound_manager
        self.keys_pressed = set()
        self.last_move_time = 0
        self.last_soft_drop_time = 0
        self.das_timer = 0
        self.das_active = False
        self.das_direction = 0
        self.soft_drop_active = False
    
    def handle_input(self, keys):
        """Handle player input - Game Boy style"""
        if self.game.game_over:
            return
        
        current_time = pygame.time.get_ticks()
        
        # Handle rotation (A button)
        if keys[pygame.K_UP] and pygame.K_UP not in self.keys_pressed:
            if self.game.rotate_piece():
                self.sound_manager.play_sound('rotate')
        
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
        
        # Handle soft drop (down button)
        if keys[pygame.K_DOWN]:
            if not self.soft_drop_active:
                # Start soft drop
                self.soft_drop_active = True
                self.last_soft_drop_time = current_time
                # Immediate first drop
                if self.game.soft_drop() > 0:
                    self.sound_manager.play_sound('move')
            elif current_time - self.last_soft_drop_time >= SOFT_DROP_SPEED:
                # Continue soft drop
                if self.game.soft_drop() > 0:
                    self.sound_manager.play_sound('move')
                self.last_soft_drop_time = current_time
        else:
            self.soft_drop_active = False
        
        # Update pressed keys
        self.keys_pressed = {key for key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_DOWN, pygame.K_UP] if keys[key]}
    
    def _handle_horizontal_movement(self, direction, current_time):
        """Handle horizontal movement with DAS (Game Boy style)"""
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
                if current_time - self.das_timer >= DAS_DELAY:
                    self.das_active = True
                    self.das_timer = current_time
            else:
                # DAS is active, check for repeat
                if current_time - self.das_timer >= DAS_SPEED:
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
        self.soft_drop_active = False
