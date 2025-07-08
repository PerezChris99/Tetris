#!/usr/bin/env python3
"""Test script to verify that line clearing doesn't crash the game"""

import pygame
from game import TetrisGame
from sounds import SoundManager

def test_line_clearing():
    """Test that line clearing works without crashes"""
    print("Testing line clearing functionality...")
    
    # Initialize pygame (needed for sound manager)
    pygame.init()
    
    # Create sound manager and game
    sound_manager = SoundManager()
    game = TetrisGame(start_level=0, sound_manager=sound_manager)
    
    # Create a test grid with some full lines
    print("Setting up test grid with full lines...")
    for row in range(15, 20):  # Fill bottom 5 rows
        for col in range(10):
            game.grid[row][col] = 1
            game.grid_colors[row][col] = (255, 255, 255)  # White
    
    # Clear the last column in a few rows to make them not full
    game.grid[15][9] = 0
    game.grid[16][9] = 0
    game.grid[17][9] = 0
    
    print("Grid setup complete. Testing line clearing...")
    
    # Test clearing lines
    try:
        lines_cleared = game.clear_lines()
        print(f"Lines cleared: {lines_cleared}")
        print("✓ SUCCESS: Line clearing works without crashes!")
        return True
    except Exception as e:
        print(f"✗ FAILED: Line clearing crashed with error: {e}")
        return False

if __name__ == "__main__":
    success = test_line_clearing()
    pygame.quit()
    if success:
        print("\nAll tests passed! The game should now work properly.")
    else:
        print("\nThere are still issues with the game.")
