import pygame
import sys
import time
from config import *
from player import Player
from ai_player import AIPlayer
from sounds import SoundManager

class TetrisBattle:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tetris Battle - Human vs AI")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, FONT_LARGE)
        self.font_medium = pygame.font.Font(None, FONT_MEDIUM)
        self.font_small = pygame.font.Font(None, FONT_SMALL)
        
        # Game state
        self.sound_manager = SoundManager()
        self.player = Player(self.sound_manager)
        self.ai_player = AIPlayer(self.sound_manager)
        
        # Round system
        self.current_round = 1
        self.player_wins = 0
        self.ai_wins = 0
        self.round_start_time = 0
        self.round_duration = ROUND_TIME_LIMIT
        self.game_state = "playing"  # playing, round_end, game_end
        self.round_end_time = 0
        self.round_winner = None
        
        self.start_round()
    
    def start_round(self):
        """Start a new round"""
        self.player.reset()
        self.ai_player.reset()
        self.round_start_time = time.time()
        self.game_state = "playing"
        self.round_winner = None
        print(f"Starting Round {self.current_round}")
    
    def update(self, dt):
        """Update game state"""
        if self.game_state == "playing":
            # Update players
            self.player.update(dt)
            self.ai_player.update(dt)
            
            # Check for round end conditions
            current_time = time.time()
            time_elapsed = current_time - self.round_start_time
            
            # Check if either player died
            if self.player.game.game_over and not self.ai_player.game.game_over:
                self.end_round("AI")
            elif self.ai_player.game.game_over and not self.player.game.game_over:
                self.end_round("Player")
            elif self.player.game.game_over and self.ai_player.game.game_over:
                # Both died, whoever has higher score wins
                if self.player.game.score > self.ai_player.game.score:
                    self.end_round("Player")
                elif self.ai_player.game.score > self.player.game.score:
                    self.end_round("AI")
                else:
                    self.end_round("Draw")
            elif time_elapsed >= self.round_duration:
                # Time limit reached
                if self.player.game.score > self.ai_player.game.score:
                    self.end_round("Player")
                elif self.ai_player.game.score > self.player.game.score:
                    self.end_round("AI")
                else:
                    self.end_round("Draw")
        
        elif self.game_state == "round_end":
            # Wait for a few seconds before starting next round
            if time.time() - self.round_end_time >= 3:
                if self.player_wins >= ROUNDS_TO_WIN or self.ai_wins >= ROUNDS_TO_WIN:
                    self.game_state = "game_end"
                else:
                    self.current_round += 1
                    self.start_round()
    
    def end_round(self, winner):
        """End the current round"""
        self.round_winner = winner
        self.round_end_time = time.time()
        self.game_state = "round_end"
        
        if winner == "Player":
            self.player_wins += 1
            self.sound_manager.play_sound('win')
        elif winner == "AI":
            self.ai_wins += 1
            self.sound_manager.play_sound('lose')
        
        print(f"Round {self.current_round} ended. Winner: {winner}")
        print(f"Score - Player: {self.player_wins}, AI: {self.ai_wins}")
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_r and self.game_state == "game_end":
                    # Restart game
                    self.current_round = 1
                    self.player_wins = 0
                    self.ai_wins = 0
                    self.start_round()
                elif event.key == pygame.K_m:
                    # Toggle sound
                    self.sound_manager.toggle_sound()
        
        # Handle player input
        if self.game_state == "playing":
            keys = pygame.key.get_pressed()
            self.player.handle_input(keys)
        
        return True
    
    def draw(self):
        """Draw everything"""
        self.screen.fill(UI_BACKGROUND)
        
        # Draw header
        self.draw_header()
        
        # Draw game grids
        self.draw_game_grid(self.player.game, PLAYER_GRID_X, PLAYER_GRID_Y, "PLAYER")
        self.draw_game_grid(self.ai_player.game, AI_GRID_X, AI_GRID_Y, "AI")
        
        # Draw UI elements
        self.draw_scores()
        self.draw_next_pieces()
        
        # Draw game state overlays
        if self.game_state == "round_end":
            self.draw_round_end_overlay()
        elif self.game_state == "game_end":
            self.draw_game_end_overlay()
        
        # Draw time remaining
        if self.game_state == "playing":
            self.draw_time_remaining()
        
        pygame.display.flip()
    
    def draw_header(self):
        """Draw the header with round info"""
        header_text = f"Round {self.current_round} - Player: {self.player_wins} | AI: {self.ai_wins}"
        text_surface = self.font_medium.render(header_text, True, UI_TEXT)
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, 30))
        self.screen.blit(text_surface, text_rect)
    
    def draw_game_grid(self, game, grid_x, grid_y, label):
        """Draw a game grid"""
        # Draw label
        label_surface = self.font_medium.render(label, True, UI_TEXT)
        label_rect = label_surface.get_rect(center=(grid_x + GRID_WIDTH * CELL_SIZE // 2, grid_y - 30))
        self.screen.blit(label_surface, label_rect)
        
        # Draw grid background
        grid_rect = pygame.Rect(grid_x, grid_y, GRID_WIDTH * CELL_SIZE, GRID_HEIGHT * CELL_SIZE)
        pygame.draw.rect(self.screen, BLACK, grid_rect)
        pygame.draw.rect(self.screen, WHITE, grid_rect, 2)
        
        # Draw placed blocks
        for row in range(GRID_HEIGHT):
            for col in range(GRID_WIDTH):
                if game.grid[row][col] != 0:
                    block_rect = pygame.Rect(
                        grid_x + col * CELL_SIZE,
                        grid_y + row * CELL_SIZE,
                        CELL_SIZE,
                        CELL_SIZE
                    )
                    pygame.draw.rect(self.screen, game.grid_colors[row][col], block_rect)
                    pygame.draw.rect(self.screen, WHITE, block_rect, 1)
        
        # Draw current piece
        if game.current_piece and not game.game_over:
            # Draw ghost piece
            ghost = game.get_ghost_piece()
            if ghost:
                for block_x, block_y in ghost.get_blocks():
                    if 0 <= block_x < GRID_WIDTH and 0 <= block_y < GRID_HEIGHT:
                        block_rect = pygame.Rect(
                            grid_x + block_x * CELL_SIZE,
                            grid_y + block_y * CELL_SIZE,
                            CELL_SIZE,
                            CELL_SIZE
                        )
                        pygame.draw.rect(self.screen, COLORS['GHOST'], block_rect)
                        pygame.draw.rect(self.screen, WHITE, block_rect, 1)
            
            # Draw current piece
            for block_x, block_y in game.current_piece.get_blocks():
                if 0 <= block_x < GRID_WIDTH and 0 <= block_y < GRID_HEIGHT:
                    block_rect = pygame.Rect(
                        grid_x + block_x * CELL_SIZE,
                        grid_y + block_y * CELL_SIZE,
                        CELL_SIZE,
                        CELL_SIZE
                    )
                    pygame.draw.rect(self.screen, game.current_piece.color, block_rect)
                    pygame.draw.rect(self.screen, WHITE, block_rect, 1)
        
        # Draw game over overlay
        if game.game_over:
            overlay = pygame.Surface((GRID_WIDTH * CELL_SIZE, GRID_HEIGHT * CELL_SIZE))
            overlay.set_alpha(128)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (grid_x, grid_y))
            
            game_over_text = self.font_medium.render("GAME OVER", True, UI_TEXT)
            text_rect = game_over_text.get_rect(center=(
                grid_x + GRID_WIDTH * CELL_SIZE // 2,
                grid_y + GRID_HEIGHT * CELL_SIZE // 2
            ))
            self.screen.blit(game_over_text, text_rect)
    
    def draw_scores(self):
        """Draw score information"""
        # Player score
        player_score_text = self.font_small.render(f"Score: {self.player.game.score}", True, UI_TEXT)
        player_level_text = self.font_small.render(f"Level: {self.player.game.level}", True, UI_TEXT)
        player_lines_text = self.font_small.render(f"Lines: {self.player.game.lines_cleared}", True, UI_TEXT)
        
        self.screen.blit(player_score_text, (PLAYER_GRID_X, PLAYER_GRID_Y + GRID_HEIGHT * CELL_SIZE + 10))
        self.screen.blit(player_level_text, (PLAYER_GRID_X, PLAYER_GRID_Y + GRID_HEIGHT * CELL_SIZE + 30))
        self.screen.blit(player_lines_text, (PLAYER_GRID_X, PLAYER_GRID_Y + GRID_HEIGHT * CELL_SIZE + 50))
        
        # AI score
        ai_score_text = self.font_small.render(f"Score: {self.ai_player.game.score}", True, UI_TEXT)
        ai_level_text = self.font_small.render(f"Level: {self.ai_player.game.level}", True, UI_TEXT)
        ai_lines_text = self.font_small.render(f"Lines: {self.ai_player.game.lines_cleared}", True, UI_TEXT)
        
        self.screen.blit(ai_score_text, (AI_GRID_X, AI_GRID_Y + GRID_HEIGHT * CELL_SIZE + 10))
        self.screen.blit(ai_level_text, (AI_GRID_X, AI_GRID_Y + GRID_HEIGHT * CELL_SIZE + 30))
        self.screen.blit(ai_lines_text, (AI_GRID_X, AI_GRID_Y + GRID_HEIGHT * CELL_SIZE + 50))
    
    def draw_next_pieces(self):
        """Draw next piece preview"""
        # Player next piece
        if self.player.game.next_pieces:
            next_piece = self.player.game.next_pieces[0]
            self.draw_piece_preview(next_piece, PLAYER_GRID_X - 120, PLAYER_GRID_Y + 50, "NEXT")
        
        # AI next piece
        if self.ai_player.game.next_pieces:
            next_piece = self.ai_player.game.next_pieces[0]
            self.draw_piece_preview(next_piece, AI_GRID_X + GRID_WIDTH * CELL_SIZE + 20, AI_GRID_Y + 50, "NEXT")
    
    def draw_piece_preview(self, piece, x, y, label):
        """Draw a piece preview"""
        label_surface = self.font_small.render(label, True, UI_TEXT)
        self.screen.blit(label_surface, (x, y - 20))
        
        # Draw piece
        shape = piece.get_shape()
        for row in range(len(shape)):
            for col in range(len(shape[row])):
                if shape[row][col]:
                    block_rect = pygame.Rect(
                        x + col * CELL_SIZE // 2,
                        y + row * CELL_SIZE // 2,
                        CELL_SIZE // 2,
                        CELL_SIZE // 2
                    )
                    pygame.draw.rect(self.screen, piece.color, block_rect)
                    pygame.draw.rect(self.screen, WHITE, block_rect, 1)
    
    def draw_time_remaining(self):
        """Draw time remaining in round"""
        time_elapsed = time.time() - self.round_start_time
        time_remaining = max(0, self.round_duration - time_elapsed)
        
        minutes = int(time_remaining // 60)
        seconds = int(time_remaining % 60)
        time_text = f"Time: {minutes:02d}:{seconds:02d}"
        
        time_surface = self.font_medium.render(time_text, True, UI_TEXT)
        time_rect = time_surface.get_rect(center=(SCREEN_WIDTH // 2, 60))
        self.screen.blit(time_surface, time_rect)
    
    def draw_round_end_overlay(self):
        """Draw round end overlay"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        if self.round_winner == "Draw":
            winner_text = "ROUND DRAW!"
        else:
            winner_text = f"{self.round_winner.upper()} WINS ROUND {self.current_round}!"
        
        winner_surface = self.font_large.render(winner_text, True, UI_TEXT)
        winner_rect = winner_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(winner_surface, winner_rect)
        
        score_text = f"Player: {self.player_wins}  |  AI: {self.ai_wins}"
        score_surface = self.font_medium.render(score_text, True, UI_TEXT)
        score_rect = score_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(score_surface, score_rect)
        
        if self.player_wins < ROUNDS_TO_WIN and self.ai_wins < ROUNDS_TO_WIN:
            next_text = f"Next round starting soon..."
            next_surface = self.font_small.render(next_text, True, UI_TEXT)
            next_rect = next_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
            self.screen.blit(next_surface, next_rect)
    
    def draw_game_end_overlay(self):
        """Draw game end overlay"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        if self.player_wins > self.ai_wins:
            winner_text = "PLAYER WINS THE MATCH!"
            winner_color = UI_ACCENT
        else:
            winner_text = "AI WINS THE MATCH!"
            winner_color = UI_TEXT
        
        winner_surface = self.font_large.render(winner_text, True, winner_color)
        winner_rect = winner_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(winner_surface, winner_rect)
        
        final_score_text = f"Final Score - Player: {self.player_wins}  |  AI: {self.ai_wins}"
        score_surface = self.font_medium.render(final_score_text, True, UI_TEXT)
        score_rect = score_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(score_surface, score_rect)
        
        restart_text = "Press R to restart or ESC to quit"
        restart_surface = self.font_small.render(restart_text, True, UI_TEXT)
        restart_rect = restart_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(restart_surface, restart_rect)
    
    def run(self):
        """Main game loop"""
        running = True
        while running:
            dt = self.clock.tick(60)
            
            running = self.handle_events()
            self.update(dt)
            self.draw()
        
        pygame.quit()
        sys.exit()

def main():
    """Main function"""
    game = TetrisBattle()
    game.run()

if __name__ == "__main__":
    main()
