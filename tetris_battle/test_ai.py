#!/usr/bin/env python3
"""
Simple test to verify AI is working
"""
import sys
sys.path.append('.')

import pygame
import time
from ai_player import AIPlayer
from sounds import SoundManager

def main():
    pygame.init()
    
    # Create AI player
    sound_manager = SoundManager()
    ai = AIPlayer(sound_manager, start_level=0)
    
    # Test for 30 seconds
    start_time = time.time()
    clock = pygame.time.Clock()
    
    print("Testing AI for 30 seconds...")
    print(f"Initial state: Score={ai.game.score}, Lines={ai.game.lines_cleared}, Pieces={ai.game.pieces_dropped}")
    
    last_pieces = ai.game.pieces_dropped
    last_lines = ai.game.lines_cleared
    
    while time.time() - start_time < 30:
        dt = clock.tick(60) / 1000.0
        ai.update(dt)
        
        # Check if AI made progress
        if ai.game.pieces_dropped > last_pieces:
            print(f"AI dropped piece #{ai.game.pieces_dropped} (Score: {ai.game.score}, Lines: {ai.game.lines_cleared})")
            last_pieces = ai.game.pieces_dropped
        
        if ai.game.lines_cleared > last_lines:
            print(f"AI cleared lines! Total: {ai.game.lines_cleared}")
            last_lines = ai.game.lines_cleared
        
        if ai.game.game_over:
            print("AI game over!")
            break
    
    print(f"Final state: Score={ai.game.score}, Lines={ai.game.lines_cleared}, Pieces={ai.game.pieces_dropped}")
    print("AI test completed!")

if __name__ == "__main__":
    main()
