import pygame
import time
from config import *
from player import Player
from sounds import SoundManager

class SinglePlayerTetris:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Game Boy Tetris - Single Player")
        self.clock = pygame.time.Clock()
        
        # Use small pixelated font for Game Boy feel
        self.font_large = pygame.font.Font(None, FONT_LARGE)
        self.font_medium = pygame.font.Font(None, FONT_MEDIUM)
        self.font_small = pygame.font.Font(None, FONT_SMALL)
        
        # Game state
        self.sound_manager = SoundManager()
        self.player = Player(self.sound_manager, start_level=0)
        self.game_over = False
        
        # Center the grid
        self.grid_x = (SCREEN_WIDTH - GRID_WIDTH * CELL_SIZE) // 2
        self.grid_y = 80
        
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_r and self.game_over:
                    # Restart game
                    self.restart_game()
                elif event.key == pygame.K_m:
                    # Toggle sound
                    self.sound_manager.toggle_sound()
        
        # Handle player input
        if not self.game_over:
            keys = pygame.key.get_pressed()
            self.player.handle_input(keys)
        
        return True
    
    def update(self, dt):
        """Update game state"""
        if not self.game_over:
            self.player.update(dt)
            if self.player.game.game_over:
                self.game_over = True
    
    def restart_game(self):
        """Restart the game"""
        self.player.reset()
        self.game_over = False
    
    def draw(self):
        """Draw everything - Game Boy style"""
        self.screen.fill(UI_BACKGROUND)
        
        # Draw title
        title_text = self.font_medium.render("GAME BOY TETRIS", True, UI_TEXT)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 20))
        self.screen.blit(title_text, title_rect)
        
        # Draw game grid
        self.draw_game_grid()
        
        # Draw stats
        self.draw_stats()
        
        # Draw next piece
        if self.player.game.next_piece:
            self.draw_next_piece()
        
        # Draw game over overlay
        if self.game_over:
            self.draw_game_over_overlay()
        
        pygame.display.flip()
    
    def draw_game_grid(self):
        """Draw the game grid - Game Boy style"""
        game = self.player.game
        
        # Draw grid border
        border_rect = pygame.Rect(self.grid_x - 2, self.grid_y - 2, 
                                 GRID_WIDTH * CELL_SIZE + 4, 
                                 VISIBLE_HEIGHT * CELL_SIZE + 4)
        pygame.draw.rect(self.screen, UI_BORDER, border_rect, 2)
        
        # Draw grid cells
        for row in range(VISIBLE_HEIGHT):  # Only draw visible rows
            for col in range(GRID_WIDTH):
                actual_row = row + (GRID_HEIGHT - VISIBLE_HEIGHT)
                x = self.grid_x + col * CELL_SIZE
                y = self.grid_y + row * CELL_SIZE
                
                if game.grid[actual_row][col] != 0:
                    # Check if this line is being cleared
                    if actual_row in game.clearing_lines and game.clear_animation_active:
                        # Game Boy authentic flash animation - entire line flashes white
                        flash_phase = int(game.clear_animation_timer / (game.clear_animation_duration / 4))
                        if flash_phase % 2 == 0:
                            color = GB_WHITE  # Flash to white (Game Boy style)
                        else:
                            color = TETROMINO_COLOR
                    else:
                        color = TETROMINO_COLOR
                    
                    # Draw filled cell
                    pygame.draw.rect(self.screen, color, 
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
            self.draw_piece(game.current_piece)
        
        # Draw ghost piece (only if enabled)
        if SHOW_GHOST_PIECE:
            ghost = game.get_ghost_piece()
            if ghost:
                self.draw_ghost_piece(ghost)
    
    def draw_piece(self, piece):
        """Draw a tetromino piece"""
        for block_x, block_y in piece.get_blocks():
            if block_y >= (GRID_HEIGHT - VISIBLE_HEIGHT):  # Only draw visible part
                x = self.grid_x + block_x * CELL_SIZE
                y = self.grid_y + (block_y - (GRID_HEIGHT - VISIBLE_HEIGHT)) * CELL_SIZE
                
                if 0 <= x < SCREEN_WIDTH and 0 <= y < SCREEN_HEIGHT:
                    pygame.draw.rect(self.screen, TETROMINO_COLOR, 
                                   (x, y, CELL_SIZE, CELL_SIZE))
                    pygame.draw.rect(self.screen, UI_BORDER, 
                                   (x, y, CELL_SIZE, CELL_SIZE), 1)
    
    def draw_ghost_piece(self, ghost):
        """Draw the ghost piece (preview)"""
        for block_x, block_y in ghost.get_blocks():
            if block_y >= (GRID_HEIGHT - VISIBLE_HEIGHT):  # Only draw visible part
                x = self.grid_x + block_x * CELL_SIZE
                y = self.grid_y + (block_y - (GRID_HEIGHT - VISIBLE_HEIGHT)) * CELL_SIZE
                
                if 0 <= x < SCREEN_WIDTH and 0 <= y < SCREEN_HEIGHT:
                    pygame.draw.rect(self.screen, COLORS['GHOST'], 
                                   (x, y, CELL_SIZE, CELL_SIZE))
                    pygame.draw.rect(self.screen, UI_BORDER, 
                                   (x, y, CELL_SIZE, CELL_SIZE), 1)
    
    def draw_stats(self):
        """Draw game statistics - Game Boy style"""
        game = self.player.game
        
        # Position stats to the left of the grid
        stats_x = self.grid_x - 120
        stats_y = self.grid_y + 50
        
        # Score
        score_text = self.font_small.render("SCORE", True, UI_TEXT)
        self.screen.blit(score_text, (stats_x, stats_y))
        score_value = self.font_small.render(f"{game.score:06d}", True, UI_TEXT)
        self.screen.blit(score_value, (stats_x, stats_y + 15))
        
        # Lines
        lines_text = self.font_small.render("LINES", True, UI_TEXT)
        self.screen.blit(lines_text, (stats_x, stats_y + 40))
        lines_value = self.font_small.render(f"{game.lines_cleared:03d}", True, UI_TEXT)
        self.screen.blit(lines_value, (stats_x, stats_y + 55))
        
        # Level
        level_text = self.font_small.render("LEVEL", True, UI_TEXT)
        self.screen.blit(level_text, (stats_x, stats_y + 80))
        level_value = self.font_small.render(f"{game.level:02d}", True, UI_TEXT)
        self.screen.blit(level_value, (stats_x, stats_y + 95))
    
    def draw_next_piece(self):
        """Draw the next piece preview"""
        # Position next piece to the right of the grid
        next_x = self.grid_x + GRID_WIDTH * CELL_SIZE + 20
        next_y = self.grid_y + 50
        
        next_text = self.font_small.render("NEXT", True, UI_TEXT)
        self.screen.blit(next_text, (next_x, next_y))
        
        # Draw preview box
        preview_rect = pygame.Rect(next_x, next_y + 15, 4 * CELL_SIZE, 4 * CELL_SIZE)
        pygame.draw.rect(self.screen, UI_BACKGROUND, preview_rect)
        pygame.draw.rect(self.screen, UI_BORDER, preview_rect, 1)
        
        # Draw piece
        from tetromino import Tetromino
        preview_piece = Tetromino(self.player.game.next_piece)
        preview_piece.x = 0
        preview_piece.y = 0
        
        for block_x, block_y in preview_piece.get_blocks():
            px = next_x + block_x * CELL_SIZE
            py = next_y + 15 + block_y * CELL_SIZE
            pygame.draw.rect(self.screen, TETROMINO_COLOR, 
                           (px, py, CELL_SIZE, CELL_SIZE))
            pygame.draw.rect(self.screen, UI_BORDER, 
                           (px, py, CELL_SIZE, CELL_SIZE), 1)
    
    def draw_game_over_overlay(self):
        """Draw game over overlay"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Game over text
        game_over_text = "GAME OVER"
        game_over_surface = self.font_large.render(game_over_text, True, WHITE)
        game_over_rect = game_over_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(game_over_surface, game_over_rect)
        
        # Final score
        score_text = f"SCORE: {self.player.game.score:06d}"
        score_surface = self.font_medium.render(score_text, True, WHITE)
        score_rect = score_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(score_surface, score_rect)
        
        # Lines
        lines_text = f"LINES: {self.player.game.lines_cleared:03d}"
        lines_surface = self.font_medium.render(lines_text, True, WHITE)
        lines_rect = lines_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 25))
        self.screen.blit(lines_surface, lines_rect)
        
        # Restart instruction
        restart_text = "PRESS R TO RESTART"
        restart_surface = self.font_small.render(restart_text, True, WHITE)
        restart_rect = restart_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 70))
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
    game = SinglePlayerTetris()
    game.run()

if __name__ == "__main__":
    main()
