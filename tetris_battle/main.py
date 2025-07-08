import pygame
import time
import numpy as np
from config import *
from player import Player
from ai_player import AIPlayer
from sounds import SoundManager

# Optional matplotlib import for statistics graphs
try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Note: matplotlib not installed. Statistics graphs will be disabled.")

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
        self.game_state = "playing"  # playing, paused, round_end, game_end, stats
        self.paused = False
        self.pause_time = 0
        self.round_end_time = 0
        self.round_winner = None
        self.return_to_menu = False  # Flag to return to main menu
        
        # Statistics tracking for post-round graphs
        self.round_stats = []
        self.current_round_stats = {
            'player': {'score': 0, 'lines': 0, 'pieces': 0, 'level': 0, 'time': 0},
            'ai': {'score': 0, 'lines': 0, 'pieces': 0, 'level': 0, 'time': 0}
        }
        self.round_start_time = time.time()
        
        self.start_round()
    
    def start_round(self):
        """Start a new round"""
        self.player.reset()
        self.ai_player.reset()
        self.game_state = "playing"
        self.round_winner = None
        self.round_start_time = time.time()
        
        # Reset current round stats
        self.current_round_stats = {
            'player': {'score': 0, 'lines': 0, 'pieces': 0, 'level': 0, 'time': 0},
            'ai': {'score': 0, 'lines': 0, 'pieces': 0, 'level': 0, 'time': 0}
        }
        
        print(f"Starting Round {self.current_round}")
    
    def update(self, dt):
        """Update game state"""
        if self.paused:
            return  # Skip all updates when paused
            
        if self.game_state == "playing":
            # Store previous line counts for garbage calculation
            prev_player_lines = self.player.game.lines_cleared
            prev_ai_lines = self.ai_player.game.lines_cleared
            
            self.player.update(dt)
            self.ai_player.update(dt)
            
            # Update statistics
            self.update_round_stats()
            
            # Check for line clears and send garbage (Game Boy style)
            player_lines_cleared = self.player.game.lines_cleared - prev_player_lines
            ai_lines_cleared = self.ai_player.game.lines_cleared - prev_ai_lines
            
            # Send garbage lines based on Game Boy rules
            if player_lines_cleared > 0:
                garbage_to_send = self.player.game.send_garbage_lines(player_lines_cleared)
                if garbage_to_send > 0:
                    self.ai_player.game.receive_garbage_lines(garbage_to_send)
                    print(f"Player cleared {player_lines_cleared} lines, sending {garbage_to_send} garbage to AI")
            
            if ai_lines_cleared > 0:
                garbage_to_send = self.ai_player.game.send_garbage_lines(ai_lines_cleared)
                if garbage_to_send > 0:
                    self.player.game.receive_garbage_lines(garbage_to_send)
                    print(f"AI cleared {ai_lines_cleared} lines, sending {garbage_to_send} garbage to Player")
            
            # Check for round end conditions - Only on game over (survival mode)
            if self.player.game.game_over:
                self.end_round("AI")
            elif self.ai_player.game.game_over:
                self.end_round("Player")
        
        elif self.game_state == "round_end":
            # Auto-advance after showing round end
            if time.time() - self.round_end_time > 3:
                self.show_round_stats()
        
        elif self.game_state == "stats":
            # Auto-advance after showing stats
            if time.time() - self.round_end_time > 8:
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
                    if self.paused:
                        # Show pause menu options
                        self.return_to_menu = True
                        return False
                    else:
                        # Return to main menu immediately
                        self.return_to_menu = True
                        return False
                elif event.key == pygame.K_p:
                    # Toggle pause
                    self.toggle_pause()
                elif event.key == pygame.K_r and self.game_state == "game_end":
                    # Restart game
                    self.restart_game()
                elif event.key == pygame.K_m:
                    # Toggle sound
                    self.sound_manager.toggle_sound()
        
        # Handle player input only when not paused
        if self.game_state == "playing" and not self.paused:
            keys = pygame.key.get_pressed()
            self.player.handle_input(keys)
        
        return True
    
    def toggle_pause(self):
        """Toggle pause state"""
        if self.game_state == "playing":
            self.paused = not self.paused
            if self.paused:
                self.pause_time = time.time()
            else:
                # Adjust round start time to account for paused time
                pause_duration = time.time() - self.pause_time
                self.round_start_time += pause_duration
    
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
        elif self.paused:
            self.draw_pause_overlay()
        
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
    
    def update_round_stats(self):
        """Update current round statistics"""
        round_time = time.time() - self.round_start_time
        
        self.current_round_stats['player'] = {
            'score': self.player.game.score,
            'lines': self.player.game.lines_cleared,
            'pieces': self.player.game.pieces_dropped,
            'level': self.player.game.level,
            'time': round_time
        }
        
        self.current_round_stats['ai'] = {
            'score': self.ai_player.game.score,
            'lines': self.ai_player.game.lines_cleared,
            'pieces': self.ai_player.game.pieces_dropped,
            'level': self.ai_player.game.level,
            'time': round_time
        }
    
    def show_round_stats(self):
        """Show post-round statistics (Game Boy style)"""
        # Save current round stats
        final_stats = self.current_round_stats.copy()
        final_stats['round'] = self.current_round
        final_stats['winner'] = self.round_winner
        self.round_stats.append(final_stats)
        
        # Generate and display stats graph
        self.generate_stats_graph()
        self.game_state = "stats"
    
    def generate_stats_graph(self):
        """Generate Game Boy style statistics graph"""
        if not MATPLOTLIB_AVAILABLE:
            print("Statistics graphs not available - matplotlib not installed")
            return
            
        try:
            # Create figure with Game Boy color scheme
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
            fig.patch.set_facecolor('#8BAC0F')  # Game Boy background
            
            # Set up data for graphs
            rounds = [stat['round'] for stat in self.round_stats]
            player_scores = [stat['player']['score'] for stat in self.round_stats]
            ai_scores = [stat['ai']['score'] for stat in self.round_stats]
            player_lines = [stat['player']['lines'] for stat in self.round_stats]
            ai_lines = [stat['ai']['lines'] for stat in self.round_stats]
            player_pieces = [stat['player']['pieces'] for stat in self.round_stats]
            ai_pieces = [stat['ai']['pieces'] for stat in self.round_stats]
            
            # Game Boy color palette
            gb_colors = {'player': '#0F380F', 'ai': '#306230'}
            
            # Score comparison
            ax1.plot(rounds, player_scores, 'o-', color=gb_colors['player'], label='Player', linewidth=2)
            ax1.plot(rounds, ai_scores, 's-', color=gb_colors['ai'], label='AI', linewidth=2)
            ax1.set_title('SCORE COMPARISON', fontsize=14, color='#0F380F')
            ax1.set_xlabel('Round')
            ax1.set_ylabel('Score')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            ax1.set_facecolor('#9BBC0F')
            
            # Lines cleared comparison
            ax2.plot(rounds, player_lines, 'o-', color=gb_colors['player'], label='Player', linewidth=2)
            ax2.plot(rounds, ai_lines, 's-', color=gb_colors['ai'], label='AI', linewidth=2)
            ax2.set_title('LINES CLEARED', fontsize=14, color='#0F380F')
            ax2.set_xlabel('Round')
            ax2.set_ylabel('Lines')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            ax2.set_facecolor('#9BBC0F')
            
            # Pieces per minute
            player_ppm = [stat['player']['pieces'] / max(stat['player']['time']/60, 1) for stat in self.round_stats]
            ai_ppm = [stat['ai']['pieces'] / max(stat['ai']['time']/60, 1) for stat in self.round_stats]
            
            ax3.plot(rounds, player_ppm, 'o-', color=gb_colors['player'], label='Player', linewidth=2)
            ax3.plot(rounds, ai_ppm, 's-', color=gb_colors['ai'], label='AI', linewidth=2)
            ax3.set_title('PIECES PER MINUTE', fontsize=14, color='#0F380F')
            ax3.set_xlabel('Round')
            ax3.set_ylabel('PPM')
            ax3.legend()
            ax3.grid(True, alpha=0.3)
            ax3.set_facecolor('#9BBC0F')
            
            # Win/Loss record
            player_wins = sum(1 for stat in self.round_stats if stat['winner'] == 'Player')
            ai_wins = sum(1 for stat in self.round_stats if stat['winner'] == 'AI')
            
            ax4.bar(['Player', 'AI'], [player_wins, ai_wins], 
                   color=[gb_colors['player'], gb_colors['ai']])
            ax4.set_title('WIN RECORD', fontsize=14, color='#0F380F')
            ax4.set_ylabel('Wins')
            ax4.set_facecolor('#9BBC0F')
            
            # Style all axes
            for ax in [ax1, ax2, ax3, ax4]:
                ax.tick_params(colors='#0F380F')
                ax.spines['bottom'].set_color('#0F380F')
                ax.spines['top'].set_color('#0F380F')
                ax.spines['right'].set_color('#0F380F')
                ax.spines['left'].set_color('#0F380F')
            
            plt.tight_layout()
            plt.suptitle(f'TETRIS BATTLE STATISTICS - ROUND {self.current_round}', 
                        fontsize=16, color='#0F380F', y=0.98)
            plt.show(block=False)
            
            # Keep window open for 5 seconds
            plt.pause(5)
            plt.close()
            
        except Exception as e:
            print(f"Error generating stats graph: {e}")
            # Skip stats display if matplotlib fails
            pass
    
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
