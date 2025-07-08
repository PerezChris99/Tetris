#!/usr/bin/env python3
"""
Simple AI Battle Test - Visual Verification
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
    pygame.display.set_caption("AI Battle Test")
    clock = pygame.time.Clock()
    
    # Create players
    sound_manager = SoundManager()
    player = Player(sound_manager, start_level=0)
    ai_player = AIPlayer(sound_manager, start_level=0)
    
    font = pygame.font.Font(None, 24)
    
    # Test for 60 seconds or until game over
    start_time = time.time()
    
    while time.time() - start_time < 60:
        dt = clock.tick(60) / 1000.0
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
        
        # Update players
        player.update(dt)
        ai_player.update(dt)
        
        # Check for game over
        if player.game.game_over or ai_player.game.game_over:
            break
        
        # Draw everything
        screen.fill(UI_BACKGROUND)
        
        # Draw title
        title = font.render("AI Battle Test - Player vs AI", True, UI_TEXT)
        screen.blit(title, (10, 10))
        
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
            screen.blit(text, (10, 50 + i * 25))
        
        for i, stat in enumerate(ai_stats):
            text = font.render(stat, True, UI_TEXT)
            screen.blit(text, (400, 50 + i * 25))
        
        # Draw time remaining
        time_left = 60 - (time.time() - start_time)
        time_text = font.render(f"Time: {time_left:.1f}s", True, UI_TEXT)
        screen.blit(time_text, (SCREEN_WIDTH // 2 - 50, 10))
        
        pygame.display.flip()
    
    # Show final results
    screen.fill(UI_BACKGROUND)
    result_text = font.render("Test Complete!", True, UI_TEXT)
    screen.blit(result_text, (SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT // 2))
    
    final_player = font.render(f"Player Final: {player.game.score} pts, {player.game.lines_cleared} lines", True, UI_TEXT)
    screen.blit(final_player, (10, SCREEN_HEIGHT // 2 + 50))
    
    final_ai = font.render(f"AI Final: {ai_player.game.score} pts, {ai_player.game.lines_cleared} lines", True, UI_TEXT)
    screen.blit(final_ai, (10, SCREEN_HEIGHT // 2 + 75))
    
    pygame.display.flip()
    
    # Wait for user to close
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
        clock.tick(60)

if __name__ == "__main__":
    main()
