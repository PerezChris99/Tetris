#!/usr/bin/env python3
"""
Comprehensive test for AI and Player fixes
"""
import pygame
import time
from config import *
from ai_player import AIPlayer
from player import Player
from sounds import SoundManager

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Tetris Battle - Fixed Version")
    clock = pygame.time.Clock()
    
    # Create players
    sound_manager = SoundManager()
    player = Player(sound_manager, start_level=0)
    ai_player = AIPlayer(sound_manager, start_level=0)
    
    font = pygame.font.Font(None, 24)
    
    # Test for 120 seconds or until game over
    start_time = time.time()
    
    print("Testing for 2 minutes...")
    print("Player controls:")
    print("  Arrow keys: Move/Rotate")
    print("  Down: Soft drop")
    print("  Space: Hard drop")
    print("  ESC: Quit")
    
    running = True
    while running and time.time() - start_time < 120:
        dt = clock.tick(60) / 1000.0
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Handle player input
        keys = pygame.key.get_pressed()
        player.handle_input(keys)
        
        # Update players
        player.update(dt)
        ai_player.update(dt)
        
        # Check for game over
        if player.game.game_over:
            print("Player game over!")
            break
        if ai_player.game.game_over:
            print("AI game over!")
            break
        
        # Draw everything
        screen.fill(UI_BACKGROUND)
        
        # Draw title
        title = font.render("Tetris Battle - Fixed Version", True, UI_TEXT)
        screen.blit(title, (10, 10))
        
        # Draw controls
        controls = [
            "Player: Arrows=Move/Rotate, Down=Soft Drop, Space=Hard Drop",
            "AI: Auto-playing with uniform speed"
        ]
        
        for i, control in enumerate(controls):
            text = font.render(control, True, UI_TEXT)
            screen.blit(text, (10, 30 + i * 20))
        
        # Draw player stats
        player_stats = [
            f"Player Score: {player.game.score}",
            f"Player Lines: {player.game.lines_cleared}",
            f"Player Pieces: {player.game.pieces_dropped}",
            f"Player Level: {player.game.level}"
        ]
        
        ai_stats = [
            f"AI Score: {ai_player.game.score}",
            f"AI Lines: {ai_player.game.lines_cleared}",
            f"AI Pieces: {ai_player.game.pieces_dropped}",
            f"AI Level: {ai_player.game.level}"
        ]
        
        # Draw stats
        for i, stat in enumerate(player_stats):
            text = font.render(stat, True, UI_TEXT)
            screen.blit(text, (10, 90 + i * 25))
        
        for i, stat in enumerate(ai_stats):
            text = font.render(stat, True, UI_TEXT)
            screen.blit(text, (400, 90 + i * 25))
        
        # Draw time remaining
        time_left = 120 - (time.time() - start_time)
        time_text = font.render(f"Time: {time_left:.1f}s", True, UI_TEXT)
        screen.blit(time_text, (SCREEN_WIDTH // 2 - 50, 10))
        
        # Draw AI status
        ai_status = "Thinking..." if ai_player.thinking else f"Actions: {len(ai_player.action_queue)}"
        ai_status_text = font.render(f"AI Status: {ai_status}", True, UI_TEXT)
        screen.blit(ai_status_text, (400, 200))
        
        pygame.display.flip()
    
    # Show final results
    print("\n=== FINAL RESULTS ===")
    print(f"Player: {player.game.score} points, {player.game.lines_cleared} lines, {player.game.pieces_dropped} pieces")
    print(f"AI: {ai_player.game.score} points, {ai_player.game.lines_cleared} lines, {ai_player.game.pieces_dropped} pieces")
    
    if player.game.game_over and ai_player.game.game_over:
        print("Both players lost!")
    elif player.game.game_over:
        print("AI wins!")
    elif ai_player.game.game_over:
        print("Player wins!")
    else:
        print("Test completed successfully!")
    
    pygame.quit()

if __name__ == "__main__":
    main()
