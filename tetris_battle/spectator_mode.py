"""
Spectator Mode for Tetris Battle Online Multiplayer
Allows players to watch ongoing games
"""
import pygame
import time
import threading
from typing import Dict, List, Optional, Any
from config import *
from sounds import SoundManager
from network_protocol import NetworkMessage, MessageType
from game import TetrisGame

class SpectatorMode:
    """Spectator mode for watching Tetris battles"""
    
    def __init__(self, screen: pygame.Surface, sound_manager: SoundManager):
        self.screen = screen
        self.sound_manager = sound_manager
        self.clock = pygame.time.Clock()
        
        # Fonts
        self.font_large = pygame.font.Font(None, FONT_LARGE)
        self.font_medium = pygame.font.Font(None, FONT_MEDIUM)
        self.font_small = pygame.font.Font(None, FONT_SMALL)
        
        # Spectator state
        self.spectating = False
        self.game_state = None
        self.player1_state = None
        self.player2_state = None
        self.game_info = {}
        self.round_info = {}
        
        # Chat system for spectators
        self.chat_messages = []
        self.chat_input = ""
        self.chat_active = False
        self.show_chat = True
        
        # UI state
        self.show_stats = True
        self.show_next_pieces = True
        self.camera_follow = "auto"  # auto, player1, player2
        self.ui_opacity = 0.8
        
        # Network
        self.network_manager = None
        self.player_id = None
        self.spectator_list = []
        
        # Game visualization
        self.grid_offset_x = 100
        self.grid_offset_y = 100
        self.cell_size = 25
        
        # Animation state
        self.last_update = 0
        self.animation_time = 0
        
    def set_network_manager(self, network_manager, player_id: str):
        """Set network manager and register handlers"""
        self.network_manager = network_manager
        self.player_id = player_id
        
        if network_manager:
            network_manager.register_handler(MessageType.SPECTATE_UPDATE, self._handle_spectate_update)
            network_manager.register_handler(MessageType.GAME_STATE, self._handle_game_state)
            network_manager.register_handler(MessageType.CHAT, self._handle_spectator_chat)
            network_manager.register_handler(MessageType.PLAYER_INPUT, self._handle_player_input)
            network_manager.register_handler(MessageType.LINE_CLEAR, self._handle_line_clear)
    
    def start_spectating(self, lobby_id: str):
        """Start spectating a game"""
        if self.network_manager:
            msg = NetworkMessage(MessageType.SPECTATE_REQUEST, {
                'lobby_id': lobby_id,
                'player_id': self.player_id
            })
            self.network_manager.send_message(msg)
            self.spectating = True
    
    def stop_spectating(self):
        """Stop spectating"""
        if self.network_manager and self.spectating:
            msg = NetworkMessage(MessageType.SPECTATE_STOP, {
                'player_id': self.player_id
            })
            self.network_manager.send_message(msg)
        
        self.spectating = False
        self.game_state = None
        self.player1_state = None
        self.player2_state = None
    
    def handle_input(self, event):
        """Handle spectator input"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.stop_spectating()
                return False  # Exit spectator mode
            elif event.key == pygame.K_c:
                self.show_chat = not self.show_chat
            elif event.key == pygame.K_s:
                self.show_stats = not self.show_stats
            elif event.key == pygame.K_n:
                self.show_next_pieces = not self.show_next_pieces
            elif event.key == pygame.K_1:
                self.camera_follow = "player1"
            elif event.key == pygame.K_2:
                self.camera_follow = "player2"
            elif event.key == pygame.K_a:
                self.camera_follow = "auto"
            elif event.key == pygame.K_RETURN:
                if self.chat_active:
                    self._send_chat_message()
                    self.chat_active = False
                    self.chat_input = ""
                else:
                    self.chat_active = True
            elif event.key == pygame.K_BACKSPACE and self.chat_active:
                self.chat_input = self.chat_input[:-1]
            elif self.chat_active and event.unicode.isprintable():
                if len(self.chat_input) < 100:
                    self.chat_input += event.unicode
            elif event.key == pygame.K_m:
                self.sound_manager.toggle_sound()
        
        return True
    
    def update(self, dt):
        """Update spectator mode"""
        if not self.spectating:
            return
        
        self.animation_time += dt
        
        # Request periodic updates if we're the active spectator
        current_time = time.time()
        if current_time - self.last_update > 1.0:  # Request update every second
            if self.network_manager:
                msg = NetworkMessage(MessageType.SPECTATE_UPDATE, {
                    'player_id': self.player_id
                })
                self.network_manager.send_message(msg)
            self.last_update = current_time
    
    def draw(self):
        """Draw spectator view"""
        if not self.spectating:
            return
        
        self.screen.fill((20, 20, 30))  # Dark blue background
        
        # Draw game grids
        self._draw_game_grids()
        
        # Draw UI elements
        if self.show_stats:
            self._draw_game_stats()
        
        if self.show_next_pieces:
            self._draw_next_pieces()
        
        if self.show_chat:
            self._draw_chat()
        
        # Draw spectator info
        self._draw_spectator_info()
        
        # Draw controls help
        self._draw_controls_help()
    
    def _draw_game_grids(self):
        """Draw both player grids"""
        if not self.player1_state or not self.player2_state:
            # Show waiting message
            waiting_text = self.font_large.render("Waiting for game data...", True, (255, 255, 255))
            waiting_rect = waiting_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(waiting_text, waiting_rect)
            return
        
        # Calculate grid positions
        grid_width = GRID_WIDTH * self.cell_size
        grid_height = GRID_HEIGHT * self.cell_size
        
        # Player 1 grid (left side)
        p1_x = SCREEN_WIDTH // 4 - grid_width // 2
        p1_y = self.grid_offset_y
        
        # Player 2 grid (right side)
        p2_x = 3 * SCREEN_WIDTH // 4 - grid_width // 2
        p2_y = self.grid_offset_y
        
        # Draw player 1 grid
        self._draw_player_grid(self.player1_state, p1_x, p1_y, "Player 1")
        
        # Draw player 2 grid
        self._draw_player_grid(self.player2_state, p2_x, p2_y, "Player 2")
        
        # Draw vs indicator
        vs_text = self.font_large.render("VS", True, (255, 255, 0))
        vs_rect = vs_text.get_rect(center=(SCREEN_WIDTH // 2, p1_y + grid_height // 2))
        self.screen.blit(vs_text, vs_rect)
    
    def _draw_player_grid(self, player_state: Dict, x: int, y: int, player_name: str):
        """Draw a single player's grid"""
        if not player_state:
            return
        
        grid = player_state.get('grid', [])
        current_piece = player_state.get('current_piece')
        ghost_piece = player_state.get('ghost_piece')
        
        # Draw grid background
        grid_width = GRID_WIDTH * self.cell_size
        grid_height = GRID_HEIGHT * self.cell_size
        pygame.draw.rect(self.screen, (40, 40, 50), (x, y, grid_width, grid_height))
        pygame.draw.rect(self.screen, (100, 100, 120), (x, y, grid_width, grid_height), 2)
        
        # Draw placed pieces
        for row in range(len(grid)):
            for col in range(len(grid[row])):
                if grid[row][col] != 0:
                    cell_x = x + col * self.cell_size
                    cell_y = y + row * self.cell_size
                    
                    # Get color for piece type
                    color = self._get_piece_color(grid[row][col])
                    pygame.draw.rect(self.screen, color, 
                                   (cell_x, cell_y, self.cell_size - 1, self.cell_size - 1))
        
        # Draw ghost piece
        if ghost_piece:
            self._draw_piece_on_grid(ghost_piece, x, y, alpha=100)
        
        # Draw current piece
        if current_piece:
            self._draw_piece_on_grid(current_piece, x, y)
        
        # Draw player name and info
        name_text = self.font_medium.render(player_name, True, (255, 255, 255))
        name_rect = name_text.get_rect(center=(x + grid_width // 2, y - 30))
        self.screen.blit(name_text, name_rect)
        
        # Draw score and level
        score = player_state.get('score', 0)
        level = player_state.get('level', 1)
        lines = player_state.get('lines_cleared', 0)
        
        info_y = y + grid_height + 10
        score_text = self.font_small.render(f"Score: {score:,}", True, (255, 255, 255))
        level_text = self.font_small.render(f"Level: {level}", True, (255, 255, 255))
        lines_text = self.font_small.render(f"Lines: {lines}", True, (255, 255, 255))
        
        self.screen.blit(score_text, (x, info_y))
        self.screen.blit(level_text, (x, info_y + 20))
        self.screen.blit(lines_text, (x, info_y + 40))
    
    def _draw_piece_on_grid(self, piece_data: Dict, grid_x: int, grid_y: int, alpha: int = 255):
        """Draw a tetromino piece on the grid"""
        if not piece_data:
            return
        
        shape = piece_data.get('shape', [])
        pos_x = piece_data.get('x', 0)
        pos_y = piece_data.get('y', 0)
        piece_type = piece_data.get('type', 1)
        
        color = self._get_piece_color(piece_type)
        
        # Create surface with alpha
        piece_surface = pygame.Surface((self.cell_size, self.cell_size))
        piece_surface.set_alpha(alpha)
        piece_surface.fill(color)
        
        for row in range(len(shape)):
            for col in range(len(shape[row])):
                if shape[row][col]:
                    cell_x = grid_x + (pos_x + col) * self.cell_size
                    cell_y = grid_y + (pos_y + row) * self.cell_size
                    
                    if alpha < 255:
                        self.screen.blit(piece_surface, (cell_x, cell_y))
                    else:
                        pygame.draw.rect(self.screen, color,
                                       (cell_x, cell_y, self.cell_size - 1, self.cell_size - 1))
    
    def _get_piece_color(self, piece_type: int):
        """Get color for piece type"""
        colors = {
            1: (0, 255, 255),    # I - Cyan
            2: (255, 255, 0),    # O - Yellow
            3: (128, 0, 128),    # T - Purple
            4: (0, 255, 0),      # S - Green
            5: (255, 0, 0),      # Z - Red
            6: (255, 165, 0),    # J - Orange
            7: (0, 0, 255),      # L - Blue
        }
        return colors.get(piece_type, (128, 128, 128))
    
    def _draw_game_stats(self):
        """Draw game statistics"""
        stats_x = 20
        stats_y = 20
        
        # Game info
        round_num = self.round_info.get('round', 1)
        max_rounds = self.round_info.get('max_rounds', 5)
        p1_wins = self.round_info.get('player1_wins', 0)
        p2_wins = self.round_info.get('player2_wins', 0)
        
        stats_texts = [
            f"Round {round_num}/{max_rounds}",
            f"Player 1 Wins: {p1_wins}",
            f"Player 2 Wins: {p2_wins}",
            f"Spectators: {len(self.spectator_list)}"
        ]
        
        for i, text in enumerate(stats_texts):
            rendered = self.font_small.render(text, True, (255, 255, 255))
            self.screen.blit(rendered, (stats_x, stats_y + i * 25))
    
    def _draw_next_pieces(self):
        """Draw next pieces for both players"""
        if not self.player1_state or not self.player2_state:
            return
        
        # Player 1 next piece
        p1_next = self.player1_state.get('next_piece')
        if p1_next:
            self._draw_next_piece_preview(p1_next, 50, 200, "P1 Next")
        
        # Player 2 next piece
        p2_next = self.player2_state.get('next_piece')
        if p2_next:
            self._draw_next_piece_preview(p2_next, SCREEN_WIDTH - 150, 200, "P2 Next")
    
    def _draw_next_piece_preview(self, piece_data: Dict, x: int, y: int, label: str):
        """Draw next piece preview"""
        # Label
        label_text = self.font_small.render(label, True, (255, 255, 255))
        self.screen.blit(label_text, (x, y - 20))
        
        # Piece preview
        shape = piece_data.get('shape', [])
        piece_type = piece_data.get('type', 1)
        color = self._get_piece_color(piece_type)
        
        preview_size = 15
        for row in range(len(shape)):
            for col in range(len(shape[row])):
                if shape[row][col]:
                    cell_x = x + col * preview_size
                    cell_y = y + row * preview_size
                    pygame.draw.rect(self.screen, color,
                                   (cell_x, cell_y, preview_size - 1, preview_size - 1))
    
    def _draw_chat(self):
        """Draw spectator chat"""
        chat_x = 20
        chat_y = SCREEN_HEIGHT - 200
        chat_width = 400
        chat_height = 150
        
        # Chat background
        chat_surface = pygame.Surface((chat_width, chat_height))
        chat_surface.set_alpha(int(255 * self.ui_opacity))
        chat_surface.fill((20, 20, 20))
        self.screen.blit(chat_surface, (chat_x, chat_y))
        
        # Chat border
        pygame.draw.rect(self.screen, (100, 100, 100), 
                        (chat_x, chat_y, chat_width, chat_height), 2)
        
        # Chat messages
        msg_y = chat_y + 5
        for message in self.chat_messages[-6:]:  # Show last 6 messages
            username = message.get('username', 'Unknown')
            text = message.get('text', '')
            msg_text = f"{username}: {text}"
            
            # Truncate long messages
            if len(msg_text) > 50:
                msg_text = msg_text[:47] + "..."
            
            rendered = self.font_small.render(msg_text, True, (255, 255, 255))
            self.screen.blit(rendered, (chat_x + 5, msg_y))
            msg_y += 20
        
        # Chat input
        input_y = chat_y + chat_height - 25
        if self.chat_active:
            input_text = f"Say: {self.chat_input}|"
            color = (255, 255, 0)
        else:
            input_text = "Press ENTER to chat"
            color = (150, 150, 150)
        
        input_rendered = self.font_small.render(input_text, True, color)
        self.screen.blit(input_rendered, (chat_x + 5, input_y))
    
    def _draw_spectator_info(self):
        """Draw spectator information"""
        info_x = SCREEN_WIDTH - 200
        info_y = 20
        
        info_texts = [
            "SPECTATOR MODE",
            f"Watching: {len(self.spectator_list)} viewers",
            f"Camera: {self.camera_follow}",
            ""
        ]
        
        for i, text in enumerate(info_texts):
            if text:  # Skip empty strings
                rendered = self.font_small.render(text, True, (200, 200, 200))
                self.screen.blit(rendered, (info_x, info_y + i * 20))
    
    def _draw_controls_help(self):
        """Draw control help"""
        help_x = SCREEN_WIDTH - 250
        help_y = SCREEN_HEIGHT - 150
        
        controls = [
            "ESC - Exit spectator",
            "C - Toggle chat",
            "S - Toggle stats", 
            "N - Toggle next pieces",
            "1/2/A - Camera follow",
            "M - Toggle sound"
        ]
        
        for i, control in enumerate(controls):
            rendered = self.font_small.render(control, True, (150, 150, 150))
            self.screen.blit(rendered, (help_x, help_y + i * 15))
    
    def _send_chat_message(self):
        """Send spectator chat message"""
        if self.network_manager and self.chat_input.strip():
            msg = NetworkMessage(MessageType.CHAT, {
                'username': f"Spectator_{self.player_id[:4]}",
                'text': self.chat_input.strip(),
                'is_spectator': True
            })
            self.network_manager.send_message(msg)
    
    # Network message handlers
    def _handle_spectate_update(self, message: NetworkMessage):
        """Handle spectator update"""
        data = message.data
        self.game_state = data.get('game_state')
        self.player1_state = data.get('player1_state')
        self.player2_state = data.get('player2_state')
        self.game_info = data.get('game_info', {})
        self.round_info = data.get('round_info', {})
        self.spectator_list = data.get('spectators', [])
    
    def _handle_game_state(self, message: NetworkMessage):
        """Handle game state update"""
        # Update game state for spectators
        pass
    
    def _handle_spectator_chat(self, message: NetworkMessage):
        """Handle spectator chat"""
        self.chat_messages.append(message.data)
        if len(self.chat_messages) > 50:
            self.chat_messages = self.chat_messages[-50:]
    
    def _handle_player_input(self, message: NetworkMessage):
        """Handle player input for real-time updates"""
        # Could be used for smoother spectator experience
        pass
    
    def _handle_line_clear(self, message: NetworkMessage):
        """Handle line clear effects"""
        # Could trigger visual effects for spectators
        self.sound_manager.play_sound('clear')

def main():
    """Test spectator mode"""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Tetris Battle - Spectator Mode")
    
    sound_manager = SoundManager()
    spectator = SpectatorMode(screen, sound_manager)
    
    # Mock data for testing
    spectator.spectating = True
    spectator.player1_state = {
        'grid': [[0] * GRID_WIDTH for _ in range(GRID_HEIGHT)],
        'score': 1500,
        'level': 3,
        'lines_cleared': 15,
        'current_piece': {
            'shape': [[1, 1], [1, 1]],
            'x': 4,
            'y': 2,
            'type': 2
        },
        'next_piece': {
            'shape': [[1, 1, 1, 1]],
            'type': 1
        }
    }
    spectator.player2_state = {
        'grid': [[0] * GRID_WIDTH for _ in range(GRID_HEIGHT)],
        'score': 1200,
        'level': 2,
        'lines_cleared': 12,
        'current_piece': {
            'shape': [[1, 1, 1], [0, 1, 0]],
            'x': 3,
            'y': 1,
            'type': 3
        },
        'next_piece': {
            'shape': [[1, 1], [1, 1]],
            'type': 2
        }
    }
    spectator.round_info = {
        'round': 2,
        'max_rounds': 5,
        'player1_wins': 1,
        'player2_wins': 0
    }
    
    clock = pygame.time.Clock()
    running = True
    
    while running:
        dt = clock.tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                if not spectator.handle_input(event):
                    running = False
        
        spectator.update(dt)
        spectator.draw()
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    main()
