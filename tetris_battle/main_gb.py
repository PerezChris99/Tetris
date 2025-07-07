import pygame
import time
from config import *
from player import Player
from ai_player import AIPlayer
from sounds import SoundManager

class TetrisBattle:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tetris Battle - Game Boy Style")
        self.clock = pygame.time.Clock()
        
        # Use small pixelated font for Game Boy feel
        self.font_large = pygame.font.Font(None, FONT_LARGE)
        self.font_medium = pygame.font.Font(None, FONT_MEDIUM)
        self.font_small = pygame.font.Font(None, FONT_SMALL)
        
        # Game state
        self.sound_manager = SoundManager()
        self.player = Player(self.sound_manager, start_level=0)
        self.ai_player = AIPlayer(self.sound_manager, start_level=0)
        
        # VS mode system (Game Boy style)
        self.current_round = 1
        self.player_wins = 0
        self.ai_wins = 0
        self.game_state = "playing"  # playing, round_end, game_end
        self.round_end_time = 0
        self.round_winner = None
        
        self.start_round()
    
    def start_round(self):
        """Start a new round"""
        self.player.reset()
        self.ai_player.reset()
        self.game_state = "playing"
        self.round_winner = None
        print(f"Starting Round {self.current_round}")
    
    def update(self, dt):
        """Update game state"""
        if self.game_state == "playing":
            self.player.update(dt)
            self.ai_player.update(dt)
            
            # Check for round end conditions
            if self.player.game.game_over:
                self.end_round("AI")
            elif self.ai_player.game.game_over:
                self.end_round("Player")
            elif self.player.game.lines_cleared >= LINES_TO_WIN:
                self.end_round("Player")
            elif self.ai_player.game.lines_cleared >= LINES_TO_WIN:
                self.end_round("AI")
        
        elif self.game_state == "round_end":
            # Auto-advance after showing round end
            if time.time() - self.round_end_time > 3:
                self.next_round()
    
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
        
        # Check for game end
        if self.player_wins >= ROUNDS_TO_WIN or self.ai_wins >= ROUNDS_TO_WIN:
            self.game_state = "game_end"
    
    def next_round(self):
        """Start the next round"""
        if self.game_state == "game_end":
            return
        
        self.current_round += 1
        self.start_round()
    
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
                    self.restart_game()
                elif event.key == pygame.K_m:
                    # Toggle sound
                    self.sound_manager.toggle_sound()
        
        # Handle player input
        if self.game_state == "playing":
            keys = pygame.key.get_pressed()
            self.player.handle_input(keys)
        
        return True
    
    def restart_game(self):
        """Restart the entire game"""
        self.current_round = 1
        self.player_wins = 0
        self.ai_wins = 0
        self.game_state = "playing"
        self.round_winner = None
        self.start_round()
    
    def draw(self):
        """Draw everything - Game Boy style"""
        self.screen.fill(UI_BACKGROUND)
        
        # Draw title
        title_text = self.font_medium.render("TETRIS BATTLE", True, UI_TEXT)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 20))
        self.screen.blit(title_text, title_rect)
        
        # Draw round info
        round_text = self.font_small.render(f"ROUND {self.current_round}", True, UI_TEXT)
        round_rect = round_text.get_rect(center=(SCREEN_WIDTH // 2, 45))
        self.screen.blit(round_text, round_rect)
        
        # Draw game grids
        self.draw_game_grid(self.player.game, PLAYER_GRID_X, PLAYER_GRID_Y, "PLAYER")
        self.draw_game_grid(self.ai_player.game, AI_GRID_X, AI_GRID_Y, "AI")
        
        # Draw scores and stats
        self.draw_player_stats(self.player.game, PLAYER_GRID_X, PLAYER_GRID_Y - 60, "PLAYER")
        self.draw_player_stats(self.ai_player.game, AI_GRID_X, AI_GRID_Y - 60, "AI")
        
        # Draw next pieces
        if self.player.game.next_piece:
            self.draw_next_piece(self.player.game.next_piece, PLAYER_GRID_X + GRID_WIDTH * CELL_SIZE + 10, PLAYER_GRID_Y + 50)
        if self.ai_player.game.next_piece:
            self.draw_next_piece(self.ai_player.game.next_piece, AI_GRID_X + GRID_WIDTH * CELL_SIZE + 10, AI_GRID_Y + 50)
        
        # Draw win counters
        wins_text = f"PLAYER: {self.player_wins}  AI: {self.ai_wins}"
        wins_surface = self.font_small.render(wins_text, True, UI_TEXT)
        wins_rect = wins_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
        self.screen.blit(wins_surface, wins_rect)
        
        # Draw game state overlays
        if self.game_state == "round_end":
            self.draw_round_end_overlay()
        elif self.game_state == "game_end":
            self.draw_game_end_overlay()
        
        pygame.display.flip()
    
    def draw_game_grid(self, game, grid_x, grid_y, label):
        """Draw the game grid - Game Boy style"""
        # Draw grid border
        border_rect = pygame.Rect(grid_x - 2, grid_y - 2, 
                                 GRID_WIDTH * CELL_SIZE + 4, 
                                 VISIBLE_HEIGHT * CELL_SIZE + 4)
        pygame.draw.rect(self.screen, UI_BORDER, border_rect, 2)
        
        # Draw grid cells
        for row in range(VISIBLE_HEIGHT):  # Only draw visible rows
            for col in range(GRID_WIDTH):
                actual_row = row + (GRID_HEIGHT - VISIBLE_HEIGHT)
                x = grid_x + col * CELL_SIZE
                y = grid_y + row * CELL_SIZE
                
                if game.grid[actual_row][col] != 0:
                    # Draw filled cell
                    pygame.draw.rect(self.screen, TETROMINO_COLOR, 
                                   (x, y, CELL_SIZE, CELL_SIZE))
                    pygame.draw.rect(self.screen, UI_BORDER, 
                                   (x, y, CELL_SIZE, CELL_SIZE), 1)
                else:
                    # Draw empty cell
                    pygame.draw.rect(self.screen, UI_BACKGROUND, 
                                   (x, y, CELL_SIZE, CELL_SIZE))
                    pygame.draw.rect(self.screen, GRAY, 
                                   (x, y, CELL_SIZE, CELL_SIZE), 1)
        
        # Draw current piece
        if game.current_piece:
            self.draw_piece(game.current_piece, grid_x, grid_y)
        
        # Draw ghost piece
        ghost = game.get_ghost_piece()
        if ghost:
            self.draw_ghost_piece(ghost, grid_x, grid_y)
    
    def draw_piece(self, piece, grid_x, grid_y):
        """Draw a tetromino piece"""
        for block_x, block_y in piece.get_blocks():
            if block_y >= (GRID_HEIGHT - VISIBLE_HEIGHT):  # Only draw visible part
                x = grid_x + block_x * CELL_SIZE
                y = grid_y + (block_y - (GRID_HEIGHT - VISIBLE_HEIGHT)) * CELL_SIZE
                
                if 0 <= x < SCREEN_WIDTH and 0 <= y < SCREEN_HEIGHT:
                    pygame.draw.rect(self.screen, TETROMINO_COLOR, 
                                   (x, y, CELL_SIZE, CELL_SIZE))
                    pygame.draw.rect(self.screen, UI_BORDER, 
                                   (x, y, CELL_SIZE, CELL_SIZE), 1)
    
    def draw_ghost_piece(self, ghost, grid_x, grid_y):
        """Draw the ghost piece (preview)"""
        for block_x, block_y in ghost.get_blocks():
            if block_y >= (GRID_HEIGHT - VISIBLE_HEIGHT):  # Only draw visible part
                x = grid_x + block_x * CELL_SIZE
                y = grid_y + (block_y - (GRID_HEIGHT - VISIBLE_HEIGHT)) * CELL_SIZE
                
                if 0 <= x < SCREEN_WIDTH and 0 <= y < SCREEN_HEIGHT:
                    pygame.draw.rect(self.screen, COLORS['GHOST'], 
                                   (x, y, CELL_SIZE, CELL_SIZE))
                    pygame.draw.rect(self.screen, UI_BORDER, 
                                   (x, y, CELL_SIZE, CELL_SIZE), 1)
    
    def draw_player_stats(self, game, x, y, label):
        """Draw player statistics - Game Boy style"""
        # Player label
        label_text = self.font_small.render(label, True, UI_TEXT)
        self.screen.blit(label_text, (x, y))
        
        # Score
        score_text = self.font_small.render(f"SCORE", True, UI_TEXT)
        self.screen.blit(score_text, (x, y + 15))
        score_value = self.font_small.render(f"{game.score:06d}", True, UI_TEXT)
        self.screen.blit(score_value, (x + 50, y + 15))
        
        # Lines
        lines_text = self.font_small.render(f"LINES", True, UI_TEXT)
        self.screen.blit(lines_text, (x, y + 30))
        lines_value = self.font_small.render(f"{game.lines_cleared:03d}", True, UI_TEXT)
        self.screen.blit(lines_value, (x + 50, y + 30))
        
        # Level
        level_text = self.font_small.render(f"LEVEL", True, UI_TEXT)
        self.screen.blit(level_text, (x, y + 45))
        level_value = self.font_small.render(f"{game.level:02d}", True, UI_TEXT)
        self.screen.blit(level_value, (x + 50, y + 45))
    
    def draw_next_piece(self, piece_type, x, y):
        """Draw the next piece preview"""
        next_text = self.font_small.render("NEXT", True, UI_TEXT)
        self.screen.blit(next_text, (x, y))
        
        # Draw preview box
        preview_rect = pygame.Rect(x, y + 15, 4 * CELL_SIZE, 4 * CELL_SIZE)
        pygame.draw.rect(self.screen, UI_BACKGROUND, preview_rect)
        pygame.draw.rect(self.screen, UI_BORDER, preview_rect, 1)
        
        # Draw piece
        from tetromino import Tetromino
        preview_piece = Tetromino(piece_type)
        preview_piece.x = 0
        preview_piece.y = 0
        
        for block_x, block_y in preview_piece.get_blocks():
            px = x + block_x * CELL_SIZE
            py = y + 15 + block_y * CELL_SIZE
            pygame.draw.rect(self.screen, TETROMINO_COLOR, 
                           (px, py, CELL_SIZE, CELL_SIZE))
            pygame.draw.rect(self.screen, UI_BORDER, 
                           (px, py, CELL_SIZE, CELL_SIZE), 1)
    
    def draw_round_end_overlay(self):
        """Draw round end overlay"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Round end text
        end_text = f"ROUND {self.current_round} COMPLETE"
        end_surface = self.font_large.render(end_text, True, WHITE)
        end_rect = end_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(end_surface, end_rect)
        
        # Winner text
        winner_text = f"{self.round_winner} WINS!"
        winner_surface = self.font_medium.render(winner_text, True, WHITE)
        winner_rect = winner_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(winner_surface, winner_rect)
    
    def draw_game_end_overlay(self):
        """Draw game end overlay"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Game end text
        if self.player_wins >= ROUNDS_TO_WIN:
            end_text = "PLAYER WINS!"
        else:
            end_text = "AI WINS!"
        
        end_surface = self.font_large.render(end_text, True, WHITE)
        end_rect = end_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(end_surface, end_rect)
        
        # Final score
        score_text = f"FINAL SCORE: {self.player_wins} - {self.ai_wins}"
        score_surface = self.font_medium.render(score_text, True, WHITE)
        score_rect = score_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(score_surface, score_rect)
        
        # Restart instruction
        restart_text = "PRESS R TO RESTART"
        restart_surface = self.font_small.render(restart_text, True, WHITE)
        restart_rect = restart_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(restart_surface, restart_rect)
    
    def run(self):
        """Main game loop"""
        running = True
        while running:
            dt = self.clock.tick(60) / 1000.0
            
            running = self.handle_events()
            self.update(dt)
            self.draw()
        
        pygame.quit()

def main():
    """Main function"""
    game = TetrisBattle()
    game.run()

if __name__ == "__main__":
    main()
