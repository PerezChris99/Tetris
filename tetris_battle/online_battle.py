"""
Online Tetris Battle - Network Multiplayer Implementation
Allows two players to battle over the internet
"""
import pygame
import time
import sys
import threading
import socket
import uuid
from typing import Optional
from config import *
from network_player import NetworkPlayer
from sounds import SoundManager
from network_protocol import NetworkClient, NetworkServer, NetworkMessage, MessageType

class OnlineTetrisBattle:
    """Online multiplayer Tetris battle game"""
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tetris Battle - Online Multiplayer")
        self.clock = pygame.time.Clock()
        
        # Fonts
        self.font_large = pygame.font.Font(None, FONT_LARGE)
        self.font_medium = pygame.font.Font(None, FONT_MEDIUM)
        self.font_small = pygame.font.Font(None, FONT_SMALL)
        
        # Game state
        self.sound_manager = SoundManager()
        self.player_id = str(uuid.uuid4())[:8]  # Generate unique player ID
        
        # Network components
        self.network_manager = None
        self.is_host = False
        self.connection_established = False
        
        # Game components
        self.local_player = None
        self.remote_player = None
        
        # Game state
        self.game_state = "menu"  # menu, connecting, waiting, ready, playing, round_end, game_end
        self.current_round = 1
        self.local_wins = 0
        self.remote_wins = 0
        self.round_end_time = 0
        self.round_winner = None
        self.connection_status = "Not connected"
        self.status_message = ""
        
        # UI state
        self.menu_selection = 0
        self.menu_options = ["Host Game", "Join Game", "Back to Local"]
        self.input_text = ""
        self.input_active = False
        self.input_label = ""
        
        # Connection info
        self.host_ip = ""
        self.host_port = 0
        
        print(f"Player ID: {self.player_id}")
    
    def run(self):
        """Main game loop"""
        running = True
        while running:
            dt = self.clock.tick(60) / 1000.0
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if not self._handle_keydown(event):
                        running = False
            
            self.update(dt)
            self.draw()
        
        self.cleanup()
        pygame.quit()
    
    def _handle_keydown(self, event) -> bool:
        """Handle keyboard input"""
        if event.key == pygame.K_ESCAPE:
            if self.game_state == "menu":
                return False  # Exit game
            else:
                self._return_to_menu()
                return True
        
        if self.game_state == "menu":
            return self._handle_menu_input(event)
        elif self.game_state in ["connecting", "waiting"]:
            return self._handle_connection_input(event)
        elif self.game_state == "playing":
            return self._handle_game_input(event)
        elif self.game_state in ["round_end", "game_end"]:
            return self._handle_end_screen_input(event)
        
        return True
    
    def _handle_menu_input(self, event) -> bool:
        """Handle menu input"""
        if event.key == pygame.K_UP:
            self.menu_selection = (self.menu_selection - 1) % len(self.menu_options)
        elif event.key == pygame.K_DOWN:
            self.menu_selection = (self.menu_selection + 1) % len(self.menu_options)
        elif event.key == pygame.K_RETURN:
            self._select_menu_option()
        
        return True
    
    def _handle_connection_input(self, event) -> bool:
        """Handle connection screen input"""
        if event.key == pygame.K_RETURN and self.input_active:
            self._confirm_input()
        elif event.key == pygame.K_BACKSPACE and self.input_active:
            self.input_text = self.input_text[:-1]
        elif self.input_active and event.unicode.isprintable():
            if len(self.input_text) < 50:  # Limit input length
                self.input_text += event.unicode
        
        return True
    
    def _handle_game_input(self, event) -> bool:
        """Handle in-game input"""
        if event.key == pygame.K_m:
            self.sound_manager.toggle_sound()
        elif event.key == pygame.K_r and self.game_state == "game_end":
            self._restart_game()
        
        return True
    
    def _handle_end_screen_input(self, event) -> bool:
        """Handle end screen input"""
        if event.key == pygame.K_r:
            if self.game_state == "round_end":
                self._start_next_round()
            elif self.game_state == "game_end":
                self._restart_game()
        elif event.key == pygame.K_m:
            self.sound_manager.toggle_sound()
        
        return True
    
    def _select_menu_option(self):
        """Handle menu option selection"""
        option = self.menu_options[self.menu_selection]
        
        if option == "Host Game":
            self._start_hosting()
        elif option == "Join Game":
            self._start_joining()
        elif option == "Back to Local":
            # Exit to main menu or local game
            from main import main as local_main
            pygame.quit()
            local_main()
    
    def _start_hosting(self):
        """Start hosting a game"""
        self.is_host = True
        self.game_state = "connecting"
        self.connection_status = "Starting server..."
        self.status_message = "Setting up server..."
        
        # Start server in background thread
        server_thread = threading.Thread(target=self._setup_server, daemon=True)
        server_thread.start()
    
    def _setup_server(self):
        """Setup server (runs in background thread)"""
        try:
            self.network_manager = NetworkServer(self.player_id)
            port = self.network_manager.start_server(0)  # Use random available port
            
            if port:
                self.host_port = port
                # Get local IP address
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                        s.connect(("8.8.8.8", 80))
                        self.host_ip = s.getsockname()[0]
                except:
                    self.host_ip = "127.0.0.1"
                
                self.connection_status = f"Server running on {self.host_ip}:{port}"
                self.status_message = f"Waiting for opponent to connect...\\nShare this info:\\nIP: {self.host_ip}\\nPort: {port}"
                self._setup_network_handlers()
                
            else:
                self.connection_status = "Failed to start server"
                self.status_message = "Could not start server. Press ESC to return to menu."
                
        except Exception as e:
            self.connection_status = f"Server error: {e}"
            self.status_message = "Server setup failed. Press ESC to return to menu."
    
    def _start_joining(self):
        """Start joining a game"""
        self.is_host = False
        self.game_state = "connecting"
        self.connection_status = "Enter connection details"
        self.input_active = True
        self.input_label = "Enter host IP address:"
        self.input_text = ""
    
    def _confirm_input(self):
        """Handle input confirmation"""
        if self.input_label == "Enter host IP address:":
            self.host_ip = self.input_text.strip()
            self.input_text = ""
            self.input_label = "Enter port number:"
        elif self.input_label == "Enter port number:":
            try:
                self.host_port = int(self.input_text.strip())
                self.input_active = False
                self._connect_to_server()
            except ValueError:
                self.status_message = "Invalid port number. Please enter a valid number."
                self.input_text = ""
    
    def _connect_to_server(self):
        """Connect to server"""
        self.connection_status = "Connecting..."
        self.status_message = f"Connecting to {self.host_ip}:{self.host_port}..."
        
        # Connect in background thread
        connect_thread = threading.Thread(target=self._do_connect, daemon=True)
        connect_thread.start()
    
    def _do_connect(self):
        """Perform connection (runs in background thread)"""
        try:
            self.network_manager = NetworkClient(self.player_id)
            
            if self.network_manager.connect(self.host_ip, self.host_port):
                self.connection_status = f"Connected to {self.host_ip}:{self.host_port}"
                self.status_message = "Connected! Waiting for game to start..."
                self.connection_established = True
                self._setup_network_handlers()
            else:
                self.connection_status = "Connection failed"
                self.status_message = "Could not connect to server. Press ESC to return to menu."
                
        except Exception as e:
            self.connection_status = f"Connection error: {e}"
            self.status_message = "Connection failed. Press ESC to return to menu."
    
    def _setup_network_handlers(self):
        """Setup network message handlers"""
        if not self.network_manager:
            return
        
        self.network_manager.register_handler(MessageType.CONNECT, self._handle_player_connect)
        self.network_manager.register_handler(MessageType.DISCONNECT, self._handle_player_disconnect)
        self.network_manager.register_handler(MessageType.READY, self._handle_player_ready)
        self.network_manager.register_handler(MessageType.START_ROUND, self._handle_start_round)
        self.network_manager.register_handler(MessageType.END_ROUND, self._handle_end_round)
        self.network_manager.register_handler(MessageType.GAME_OVER, self._handle_game_over)
        self.network_manager.register_handler(MessageType.PING, self._handle_ping)
        self.network_manager.register_handler(MessageType.PONG, self._handle_pong)
    
    def _handle_player_connect(self, message: NetworkMessage):
        """Handle player connection"""
        if self.is_host and not self.connection_established:
            self.connection_established = True
            self.connection_status = "Player connected"
            self.status_message = "Opponent connected! Starting game..."
            self._start_game()
    
    def _handle_player_disconnect(self, message: NetworkMessage):
        """Handle player disconnection"""
        self.connection_established = False
        self.connection_status = "Player disconnected"
        self.status_message = "Opponent disconnected. Press ESC to return to menu."
        
        if self.game_state == "playing":
            self.game_state = "game_end"
            self.round_winner = "Disconnection"
    
    def _handle_player_ready(self, message: NetworkMessage):
        """Handle player ready message"""
        if self.is_host:
            self._start_round()
    
    def _handle_start_round(self, message: NetworkMessage):
        """Handle start round message"""
        self.current_round = message.data.get('round', 1)
        self._start_round()
    
    def _handle_end_round(self, message: NetworkMessage):
        """Handle end round message"""
        winner = message.data.get('winner')
        self._end_round(winner, from_network=True)
    
    def _handle_game_over(self, message: NetworkMessage):
        """Handle game over message"""
        self.game_state = "game_end"
    
    def _handle_ping(self, message: NetworkMessage):
        """Handle ping message"""
        if self.network_manager:
            pong_msg = NetworkMessage(MessageType.PONG, {})
            self.network_manager.send_message(pong_msg)
    
    def _handle_pong(self, message: NetworkMessage):
        """Handle pong message"""
        # Could track latency here if needed
        pass
    
    def _start_game(self):
        """Start the actual game"""
        self.game_state = "waiting"
        
        # Create players
        self.local_player = NetworkPlayer(self.player_id, self.sound_manager, start_level=0, is_local=True)
        self.remote_player = NetworkPlayer("remote", self.sound_manager, start_level=0, is_local=False)
        
        # Set network manager for players
        self.local_player.set_network_manager(self.network_manager)
        self.remote_player.set_network_manager(self.network_manager)
        
        # Reset game state
        self.current_round = 1
        self.local_wins = 0
        self.remote_wins = 0
        
        # Start first round
        if self.is_host:
            time.sleep(1)  # Brief delay
            self._start_round()
        else:
            # Send ready message to host
            ready_msg = NetworkMessage(MessageType.READY, {})
            self.network_manager.send_message(ready_msg)
    
    def _start_round(self):
        """Start a new round"""
        self.game_state = "playing"
        
        # Reset players
        if self.local_player:
            self.local_player.reset()
        if self.remote_player:
            self.remote_player.reset()
        
        self.round_winner = None
        
        # Notify remote player (if host)
        if self.is_host and self.network_manager:
            start_msg = NetworkMessage(MessageType.START_ROUND, {'round': self.current_round})
            self.network_manager.send_message(start_msg)
    
    def _start_next_round(self):
        """Start the next round"""
        if self.local_wins >= ROUNDS_TO_WIN or self.remote_wins >= ROUNDS_TO_WIN:
            self.game_state = "game_end"
            return
        
        self.current_round += 1
        self._start_round()
    
    def _end_round(self, winner: str, from_network: bool = False):
        """End the current round"""
        self.round_winner = winner
        self.round_end_time = time.time()
        self.game_state = "round_end"
        
        # Update win counts
        if winner == "Local" or winner == self.player_id:
            self.local_wins += 1
            if not from_network:
                self.sound_manager.play_sound('win')
        elif winner == "Remote":
            self.remote_wins += 1
            if not from_network:
                self.sound_manager.play_sound('lose')
        
        # Check for game end
        if self.local_wins >= ROUNDS_TO_WIN or self.remote_wins >= ROUNDS_TO_WIN:
            self.game_state = "game_end"
        
        # Notify remote player (if not from network)
        if not from_network and self.network_manager:
            end_msg = NetworkMessage(MessageType.END_ROUND, {'winner': winner})
            self.network_manager.send_message(end_msg)
    
    def _restart_game(self):
        """Restart the entire game"""
        self.current_round = 1
        self.local_wins = 0
        self.remote_wins = 0
        self._start_round()
    
    def _return_to_menu(self):
        """Return to main menu"""
        self.cleanup()
        self.game_state = "menu"
        self.connection_established = False
        self.connection_status = "Not connected"
        self.status_message = ""
    
    def update(self, dt: float):
        """Update game state"""
        if self.game_state == "playing":
            if self.local_player and self.remote_player:
                # Handle local player input
                keys = pygame.key.get_pressed()
                self.local_player.handle_input(keys)
                
                # Update both players
                prev_local_lines = self.local_player.game.lines_cleared
                prev_remote_lines = self.remote_player.game.lines_cleared
                
                self.local_player.update(dt)
                self.remote_player.update(dt)
                
                # Check for line clears and garbage
                local_lines_cleared = self.local_player.game.lines_cleared - prev_local_lines
                remote_lines_cleared = self.remote_player.game.lines_cleared - prev_remote_lines
                
                # Send garbage for local line clears
                if local_lines_cleared > 0:
                    self.local_player.send_garbage_to_opponent(local_lines_cleared)
                
                # Check for round end conditions
                if self.local_player.game.game_over:
                    self._end_round("Remote")
                elif self.remote_player.game.game_over:
                    self._end_round("Local")
                elif self.local_player.game.check_lines_win_condition():
                    self._end_round("Local")
                elif self.remote_player.game.check_lines_win_condition():
                    self._end_round("Remote")
        
        elif self.game_state == "round_end":
            # Auto-advance after 3 seconds
            if time.time() - self.round_end_time > 3:
                if self.local_wins >= ROUNDS_TO_WIN or self.remote_wins >= ROUNDS_TO_WIN:
                    self.game_state = "game_end"
                else:
                    self._start_next_round()
    
    def draw(self):
        """Draw the game"""
        self.screen.fill(UI_BACKGROUND)
        
        if self.game_state == "menu":
            self._draw_menu()
        elif self.game_state in ["connecting", "waiting"]:
            self._draw_connection_screen()
        elif self.game_state == "playing":
            self._draw_game()
        elif self.game_state == "round_end":
            self._draw_game()
            self._draw_round_end_overlay()
        elif self.game_state == "game_end":
            self._draw_game()
            self._draw_game_end_overlay()
        
        pygame.display.flip()
    
    def _draw_menu(self):
        """Draw the main menu"""
        # Title
        title = self.font_large.render("TETRIS BATTLE ONLINE", True, UI_TEXT)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)
        
        subtitle = self.font_medium.render("Network Multiplayer", True, UI_TEXT)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 140))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Menu options
        start_y = 220
        for i, option in enumerate(self.menu_options):
            color = WHITE if i == self.menu_selection else UI_TEXT
            text = self.font_medium.render(option, True, color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, start_y + i * 40))
            self.screen.blit(text, text_rect)
        
        # Instructions
        instructions = [
            "Use UP/DOWN arrows to navigate",
            "Press ENTER to select",
            "Press ESC to exit"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.font_small.render(instruction, True, UI_TEXT)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 400 + i * 20))
            self.screen.blit(text, text_rect)
    
    def _draw_connection_screen(self):
        """Draw connection/setup screen"""
        # Title
        title = self.font_large.render("NETWORK SETUP", True, UI_TEXT)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.screen.blit(title, title_rect)
        
        # Connection status
        status = self.font_medium.render(self.connection_status, True, UI_TEXT)
        status_rect = status.get_rect(center=(SCREEN_WIDTH // 2, 140))
        self.screen.blit(status, status_rect)
        
        # Status message (multi-line)
        if self.status_message:
            lines = self.status_message.split('\\n')
            for i, line in enumerate(lines):
                text = self.font_small.render(line, True, UI_TEXT)
                text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 180 + i * 25))
                self.screen.blit(text, text_rect)
        
        # Input field (if active)
        if self.input_active:
            # Input label
            label = self.font_medium.render(self.input_label, True, UI_TEXT)
            label_rect = label.get_rect(center=(SCREEN_WIDTH // 2, 320))
            self.screen.blit(label, label_rect)
            
            # Input box
            input_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, 350, 300, 30)
            pygame.draw.rect(self.screen, WHITE, input_rect)
            pygame.draw.rect(self.screen, BLACK, input_rect, 2)
            
            # Input text
            text_surface = self.font_small.render(self.input_text, True, BLACK)
            self.screen.blit(text_surface, (input_rect.x + 5, input_rect.y + 5))
        
        # Instructions
        instructions = "Press ESC to return to menu"
        inst_text = self.font_small.render(instructions, True, UI_TEXT)
        inst_rect = inst_text.get_rect(center=(SCREEN_WIDTH // 2, 500))
        self.screen.blit(inst_text, inst_rect)
    
    def _draw_game(self):
        """Draw the game (similar to main battle mode)"""
        if not self.local_player or not self.remote_player:
            return
        
        # Title
        title = self.font_medium.render("ONLINE TETRIS BATTLE", True, UI_TEXT)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 20))
        self.screen.blit(title, title_rect)
        
        # Round info
        round_text = self.font_small.render(f"ROUND {self.current_round}", True, UI_TEXT)
        round_rect = round_text.get_rect(center=(SCREEN_WIDTH // 2, 45))
        self.screen.blit(round_text, round_rect)
        
        # Draw game grids
        self._draw_game_grid(self.local_player.game, PLAYER_GRID_X, PLAYER_GRID_Y, "LOCAL")
        self._draw_game_grid(self.remote_player.game, AI_GRID_X, AI_GRID_Y, "REMOTE")
        
        # Draw stats
        self._draw_player_stats(self.local_player.game, PLAYER_GRID_X, PLAYER_GRID_Y - 60, "LOCAL")
        self._draw_player_stats(self.remote_player.game, AI_GRID_X, AI_GRID_Y - 60, "REMOTE")
        
        # Draw next pieces
        if self.local_player.game.next_piece:
            self._draw_next_piece(self.local_player.game.next_piece, PLAYER_GRID_X + GRID_WIDTH * CELL_SIZE + 10, PLAYER_GRID_Y + 50)
        if self.remote_player.game.next_piece:
            self._draw_next_piece(self.remote_player.game.next_piece, AI_GRID_X + GRID_WIDTH * CELL_SIZE + 10, AI_GRID_Y + 50)
        
        # Win counters
        wins_text = f"LOCAL: {self.local_wins}  REMOTE: {self.remote_wins}"
        wins_surface = self.font_small.render(wins_text, True, UI_TEXT)
        wins_rect = wins_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
        self.screen.blit(wins_surface, wins_rect)
    
    def _draw_game_grid(self, game, grid_x, grid_y, label):
        """Draw a game grid"""
        # Border
        border_rect = pygame.Rect(grid_x - 2, grid_y - 2, 
                                 GRID_WIDTH * CELL_SIZE + 4, 
                                 VISIBLE_HEIGHT * CELL_SIZE + 4)
        pygame.draw.rect(self.screen, UI_BORDER, border_rect, 2)
        
        # Grid cells
        for row in range(VISIBLE_HEIGHT):
            for col in range(GRID_WIDTH):
                actual_row = row + (GRID_HEIGHT - VISIBLE_HEIGHT)
                x = grid_x + col * CELL_SIZE
                y = grid_y + row * CELL_SIZE
                
                if game.grid[actual_row][col] != 0:
                    # Check for line clearing animation
                    if actual_row in game.clearing_lines and game.clear_animation_active:
                        flash_phase = int(game.clear_animation_timer / (game.clear_animation_duration / 4))
                        color = GB_WHITE if flash_phase % 2 == 0 else TETROMINO_COLOR
                    else:
                        color = TETROMINO_COLOR
                    
                    pygame.draw.rect(self.screen, color, (x, y, CELL_SIZE, CELL_SIZE))
                    pygame.draw.rect(self.screen, UI_BORDER, (x, y, CELL_SIZE, CELL_SIZE), 1)
                else:
                    pygame.draw.rect(self.screen, UI_BACKGROUND, (x, y, CELL_SIZE, CELL_SIZE))
                    pygame.draw.rect(self.screen, GRAY, (x, y, CELL_SIZE, CELL_SIZE), 1)
        
        # Current piece
        if game.current_piece:
            self._draw_piece(game.current_piece, grid_x, grid_y)
        
        # Ghost piece
        if SHOW_GHOST_PIECE:
            ghost = game.get_ghost_piece()
            if ghost:
                self._draw_ghost_piece(ghost, grid_x, grid_y)
    
    def _draw_piece(self, piece, grid_x, grid_y):
        """Draw a tetromino piece"""
        for block_x, block_y in piece.get_blocks():
            if block_y >= (GRID_HEIGHT - VISIBLE_HEIGHT):
                x = grid_x + block_x * CELL_SIZE
                y = grid_y + (block_y - (GRID_HEIGHT - VISIBLE_HEIGHT)) * CELL_SIZE
                
                if 0 <= x < SCREEN_WIDTH and 0 <= y < SCREEN_HEIGHT:
                    pygame.draw.rect(self.screen, TETROMINO_COLOR, (x, y, CELL_SIZE, CELL_SIZE))
                    pygame.draw.rect(self.screen, UI_BORDER, (x, y, CELL_SIZE, CELL_SIZE), 1)
    
    def _draw_ghost_piece(self, ghost, grid_x, grid_y):
        """Draw ghost piece"""
        for block_x, block_y in ghost.get_blocks():
            if block_y >= (GRID_HEIGHT - VISIBLE_HEIGHT):
                x = grid_x + block_x * CELL_SIZE
                y = grid_y + (block_y - (GRID_HEIGHT - VISIBLE_HEIGHT)) * CELL_SIZE
                
                if 0 <= x < SCREEN_WIDTH and 0 <= y < SCREEN_HEIGHT:
                    pygame.draw.rect(self.screen, COLORS['GHOST'], (x, y, CELL_SIZE, CELL_SIZE))
                    pygame.draw.rect(self.screen, UI_BORDER, (x, y, CELL_SIZE, CELL_SIZE), 1)
    
    def _draw_player_stats(self, game, x, y, label):
        """Draw player statistics"""
        # Label
        label_text = self.font_small.render(label, True, UI_TEXT)
        self.screen.blit(label_text, (x, y))
        
        # Score
        score_text = self.font_small.render("SCORE", True, UI_TEXT)
        self.screen.blit(score_text, (x, y + 15))
        score_value = self.font_small.render(f"{game.score:06d}", True, UI_TEXT)
        self.screen.blit(score_value, (x + 50, y + 15))
        
        # Lines
        lines_text = self.font_small.render("LINES", True, UI_TEXT)
        self.screen.blit(lines_text, (x, y + 30))
        lines_value = self.font_small.render(f"{game.lines_cleared:03d}", True, UI_TEXT)
        self.screen.blit(lines_value, (x + 50, y + 30))
        
        # Level
        level_text = self.font_small.render("LEVEL", True, UI_TEXT)
        self.screen.blit(level_text, (x, y + 45))
        level_value = self.font_small.render(f"{game.level:02d}", True, UI_TEXT)
        self.screen.blit(level_value, (x + 50, y + 45))
    
    def _draw_next_piece(self, piece_type, x, y):
        """Draw next piece preview"""
        next_text = self.font_small.render("NEXT", True, UI_TEXT)
        self.screen.blit(next_text, (x, y))
        
        # Preview box
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
            pygame.draw.rect(self.screen, TETROMINO_COLOR, (px, py, CELL_SIZE, CELL_SIZE))
            pygame.draw.rect(self.screen, UI_BORDER, (px, py, CELL_SIZE, CELL_SIZE), 1)
    
    def _draw_round_end_overlay(self):
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
    
    def _draw_game_end_overlay(self):
        """Draw game end overlay"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Game end text
        if self.local_wins >= ROUNDS_TO_WIN:
            end_text = "YOU WIN!"
        elif self.remote_wins >= ROUNDS_TO_WIN:
            end_text = "OPPONENT WINS!"
        else:
            end_text = "GAME END"
        
        end_surface = self.font_large.render(end_text, True, WHITE)
        end_rect = end_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(end_surface, end_rect)
        
        # Final score
        score_text = f"FINAL SCORE: {self.local_wins} - {self.remote_wins}"
        score_surface = self.font_medium.render(score_text, True, WHITE)
        score_rect = score_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(score_surface, score_rect)
        
        # Instructions
        restart_text = "PRESS R TO RESTART, ESC TO MENU"
        restart_surface = self.font_small.render(restart_text, True, WHITE)
        restart_rect = restart_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(restart_surface, restart_rect)
    
    def cleanup(self):
        """Cleanup network resources"""
        if self.network_manager:
            self.network_manager.disconnect()
            if hasattr(self.network_manager, 'stop_server'):
                self.network_manager.stop_server()
            self.network_manager = None

def main():
    """Main function for online multiplayer"""
    game = OnlineTetrisBattle()
    game.run()

if __name__ == "__main__":
    main()
