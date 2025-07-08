"""
Enhanced Online Tetris Battle with Lobby System and Spectator Mode
Advanced multiplayer implementation with matchmaking and viewing capabilities
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
from lobby_system import LobbyUI, LobbyManager
from spectator_mode import SpectatorMode

class EnhancedOnlineBattle:
    """Enhanced online multiplayer with lobby and spectator support"""
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tetris Battle - Enhanced Online Multiplayer")
        self.clock = pygame.time.Clock()
        
        # Core components
        self.sound_manager = SoundManager()
        self.player_id = str(uuid.uuid4())[:8]
        self.username = f"Player_{self.player_id}"
        
        # UI systems
        self.lobby_ui = LobbyUI(self.screen, self.sound_manager)
        self.spectator_mode = SpectatorMode(self.screen, self.sound_manager)
        
        # Network components
        self.network_manager = None
        self.lobby_manager = LobbyManager()  # For hosting
        self.is_host = False
        self.connection_established = False
        
        # Game components
        self.local_player = None
        self.remote_player = None
        
        # Game state management
        self.mode = "main_menu"  # main_menu, lobby, game, spectator
        self.game_state = "menu"  # menu, lobby, playing, round_end, game_end
        self.current_round = 1
        self.max_rounds = 5
        self.local_wins = 0
        self.remote_wins = 0
        self.round_end_time = 0
        self.round_winner = None
        
        # UI state
        self.main_menu_selection = 0
        self.main_menu_options = [
            "Quick Match",
            "Browse Lobbies", 
            "Create Lobby",
            "Spectate Games",
            "Settings",
            "Back to Local"
        ]
        
        # Spectator list for hosted games
        self.spectators = {}
        
        print(f"Enhanced Online Battle initialized - Player ID: {self.player_id}")
    
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            dt = self.clock.tick(60) / 1000.0
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if not self._handle_input(event):
                        running = False
            
            self.update(dt)
            self.draw()
            pygame.display.flip()
        
        self.cleanup()
        pygame.quit()
    
    def _handle_input(self, event) -> bool:
        """Route input to appropriate handler"""
        if event.key == pygame.K_ESCAPE:
            return self._handle_escape()
        
        if self.mode == "main_menu":
            return self._handle_main_menu_input(event)
        elif self.mode == "lobby":
            self.lobby_ui.handle_input(event)
            return True
        elif self.mode == "game":
            return self._handle_game_input(event)
        elif self.mode == "spectator":
            return self.spectator_mode.handle_input(event)
        
        return True
    
    def _handle_escape(self) -> bool:
        """Handle escape key based on current mode"""
        if self.mode == "main_menu":
            return False  # Exit application
        elif self.mode == "lobby":
            self._return_to_main_menu()
        elif self.mode == "game":
            self._return_to_lobby()
        elif self.mode == "spectator":
            self.spectator_mode.stop_spectating()
            self._return_to_main_menu()
        
        return True
    
    def _handle_main_menu_input(self, event) -> bool:
        """Handle main menu input"""
        if event.key == pygame.K_UP:
            self.main_menu_selection = (self.main_menu_selection - 1) % len(self.main_menu_options)
        elif event.key == pygame.K_DOWN:
            self.main_menu_selection = (self.main_menu_selection + 1) % len(self.main_menu_options)
        elif event.key == pygame.K_RETURN:
            return self._select_main_menu_option()
        
        return True
    
    def _handle_game_input(self, event) -> bool:
        """Handle in-game input"""
        if self.local_player and self.game_state == "playing":
            keys = pygame.key.get_pressed()
            self.local_player.handle_input(keys)
        
        if event.key == pygame.K_m:
            self.sound_manager.toggle_sound()
        elif event.key == pygame.K_r and self.game_state in ["round_end", "game_end"]:
            self._restart_game()
        
        return True
    
    def _select_main_menu_option(self) -> bool:
        """Handle main menu option selection"""
        option = self.main_menu_options[self.main_menu_selection]
        
        if option == "Quick Match":
            self._start_quick_match()
        elif option == "Browse Lobbies":
            self._browse_lobbies()
        elif option == "Create Lobby":
            self._create_lobby()
        elif option == "Spectate Games":
            self._spectate_games()
        elif option == "Settings":
            self._open_settings()
        elif option == "Back to Local":
            return False  # Exit to local game
        
        return True
    
    def _start_quick_match(self):
        """Start quick matchmaking"""
        # For now, redirect to browse lobbies
        # In a full implementation, this would find/create matches automatically
        self._browse_lobbies()
    
    def _browse_lobbies(self):
        """Enter lobby browser"""
        self.mode = "lobby"
        self.lobby_ui.state = "lobby_list"
        self._setup_client_connection()
    
    def _create_lobby(self):
        """Enter lobby creation"""
        self.mode = "lobby"
        self.lobby_ui.state = "create_lobby"
        self._setup_host_connection()
    
    def _spectate_games(self):
        """Enter spectator mode"""
        self.mode = "lobby"
        self.lobby_ui.state = "lobby_list"
        # The lobby UI will handle switching to spectator mode when selecting a lobby
        self._setup_client_connection()
    
    def _open_settings(self):
        """Open settings menu"""
        # TODO: Implement settings menu
        pass
    
    def _setup_host_connection(self):
        """Setup as host"""
        self.is_host = True
        
        def setup_server():
            try:
                self.network_manager = NetworkServer(self.player_id)
                port = self.network_manager.start_server(0)
                
                if port:
                    self._setup_network_handlers()
                    
                    # Get local IP
                    try:
                        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                            s.connect(("8.8.8.8", 80))
                            host_ip = s.getsockname()[0]
                    except:
                        host_ip = "127.0.0.1"
                    
                    print(f"Server started on {host_ip}:{port}")
                    
                    # Set up lobby UI with network manager
                    self.lobby_ui.set_network_manager(self.network_manager)
                    
            except Exception as e:
                print(f"Failed to setup server: {e}")
        
        threading.Thread(target=setup_server, daemon=True).start()
    
    def _setup_client_connection(self):
        """Setup as client (for browsing/joining)"""
        self.is_host = False
        # For demo purposes, we'll create a mock network manager
        # In real implementation, this would connect to a lobby server
        
        # Set up lobby UI (without network for now)
        # self.lobby_ui.set_network_manager(None)
    
    def _setup_network_handlers(self):
        """Setup network message handlers"""
        if not self.network_manager:
            return
        
        # Lobby handlers
        self.network_manager.register_handler(MessageType.LOBBY_CREATE, self._handle_lobby_create)
        self.network_manager.register_handler(MessageType.LOBBY_JOIN, self._handle_lobby_join)
        self.network_manager.register_handler(MessageType.LOBBY_LEAVE, self._handle_lobby_leave)
        self.network_manager.register_handler(MessageType.READY, self._handle_player_ready)
        
        # Spectator handlers
        self.network_manager.register_handler(MessageType.SPECTATE_REQUEST, self._handle_spectate_request)
        self.network_manager.register_handler(MessageType.SPECTATE_STOP, self._handle_spectate_stop)
        
        # Game handlers
        self.network_manager.register_handler(MessageType.PLAYER_INPUT, self._handle_player_input)
        self.network_manager.register_handler(MessageType.GAME_STATE, self._handle_game_state)
        self.network_manager.register_handler(MessageType.LINE_CLEAR, self._handle_line_clear)
        
        # Chat handlers
        self.network_manager.register_handler(MessageType.CHAT, self._handle_chat)
        self.network_manager.register_handler(MessageType.LOBBY_CHAT, self._handle_lobby_chat)
    
    def _return_to_main_menu(self):
        """Return to main menu"""
        if self.network_manager:
            self.network_manager.disconnect()
            self.network_manager = None
        
        self.mode = "main_menu"
        self.game_state = "menu"
        self.connection_established = False
    
    def _return_to_lobby(self):
        """Return to lobby from game"""
        self.mode = "lobby"
        self.game_state = "menu"
        # Reset game state but keep network connection
    
    def update(self, dt):
        """Update game state"""
        if self.mode == "game":
            self._update_game(dt)
        elif self.mode == "spectator":
            self.spectator_mode.update(dt)
    
    def _update_game(self, dt):
        """Update game logic"""
        if self.game_state != "playing":
            return
        
        # Update local player
        if self.local_player:
            self.local_player.update(dt)
            
            # Send game state updates
            if self.network_manager and time.time() * 1000 - self.local_player.last_state_update > 100:
                self._send_game_state_update()
                self.local_player.last_state_update = time.time() * 1000
        
        # Update remote player
        if self.remote_player:
            self.remote_player.update(dt)
        
        # Check for game end conditions
        self._check_game_end()
        
        # Update spectators with game state
        if self.is_host and self.spectators:
            self._update_spectators()
    
    def draw(self):
        """Draw current mode"""
        self.screen.fill((0, 0, 0))
        
        if self.mode == "main_menu":
            self._draw_main_menu()
        elif self.mode == "lobby":
            self.lobby_ui.draw()
        elif self.mode == "game":
            self._draw_game()
        elif self.mode == "spectator":
            self.spectator_mode.draw()
    
    def _draw_main_menu(self):
        """Draw main menu"""
        # Title
        title = pygame.font.Font(None, 72).render("TETRIS BATTLE", True, (255, 255, 255))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)
        
        subtitle = pygame.font.Font(None, 36).render("Enhanced Online Multiplayer", True, (150, 150, 255))
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Menu options
        start_y = 250
        for i, option in enumerate(self.main_menu_options):
            color = (255, 255, 0) if i == self.main_menu_selection else (255, 255, 255)
            option_text = pygame.font.Font(None, 48).render(option, True, color)
            option_rect = option_text.get_rect(center=(SCREEN_WIDTH // 2, start_y + i * 60))
            self.screen.blit(option_text, option_rect)
        
        # Instructions
        instructions = [
            "↑↓ Navigate  ENTER Select  ESC Exit",
            "",
            "New Features:",
            "• Lobby System with Chat",
            "• Spectator Mode", 
            "• Enhanced Matchmaking",
            "• Real-time Game Viewing"
        ]
        
        instr_y = SCREEN_HEIGHT - 200
        for instruction in instructions:
            color = (200, 200, 200) if instruction.startswith("•") else (150, 150, 150)
            if instruction == "New Features:":
                color = (255, 255, 100)
            
            instr_text = pygame.font.Font(None, 24).render(instruction, True, color)
            instr_rect = instr_text.get_rect(center=(SCREEN_WIDTH // 2, instr_y))
            self.screen.blit(instr_text, instr_rect)
            instr_y += 25
    
    def _draw_game(self):
        """Draw game screen"""
        # This would contain the actual Tetris game rendering
        # For now, show a placeholder
        game_text = pygame.font.Font(None, 48).render("GAME IN PROGRESS", True, (255, 255, 255))
        game_rect = game_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(game_text, game_rect)
        
        # Show round info
        round_text = f"Round {self.current_round}/{self.max_rounds}"
        round_rendered = pygame.font.Font(None, 36).render(round_text, True, (255, 255, 255))
        round_rect = round_rendered.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.screen.blit(round_rendered, round_rect)
        
        # Show wins
        wins_text = f"You: {self.local_wins}  Opponent: {self.remote_wins}"
        wins_rendered = pygame.font.Font(None, 24).render(wins_text, True, (255, 255, 255))
        wins_rect = wins_rendered.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(wins_rendered, wins_rect)
        
        # Show spectator count if host
        if self.is_host and self.spectators:
            spec_text = f"Spectators: {len(self.spectators)}"
            spec_rendered = pygame.font.Font(None, 24).render(spec_text, True, (200, 200, 200))
            self.screen.blit(spec_rendered, (SCREEN_WIDTH - 150, 20))
    
    # Network message handlers
    def _handle_lobby_create(self, message: NetworkMessage):
        """Handle lobby creation"""
        player_id = message.player_id
        data = message.data
        
        lobby = self.lobby_manager.create_lobby(
            host_id=player_id,
            username=data.get('username', f'Player_{player_id}'),
            lobby_name=data.get('name', 'New Lobby'),
            max_players=data.get('max_players', 2),
            max_spectators=data.get('max_spectators', 10),
            password=data.get('password', '')
        )
        
        # Send lobby update to creator
        self._send_lobby_update(lobby.lobby_id)
    
    def _handle_lobby_join(self, message: NetworkMessage):
        """Handle lobby join request"""
        player_id = message.player_id
        data = message.data
        
        lobby = self.lobby_manager.join_lobby(
            lobby_id=data.get('lobby_id'),
            player_id=player_id,
            username=data.get('username', f'Player_{player_id}'),
            password=data.get('password', ''),
            as_spectator=data.get('as_spectator', False)
        )
        
        if lobby:
            self._send_lobby_update(lobby.lobby_id)
        else:
            # Send error message
            error_msg = NetworkMessage(MessageType.ERROR, {
                'message': 'Failed to join lobby'
            })
            # Send to requesting player
    
    def _handle_lobby_leave(self, message: NetworkMessage):
        """Handle lobby leave"""
        player_id = message.player_id
        data = message.data
        
        lobby_id = data.get('lobby_id')
        if self.lobby_manager.leave_lobby(lobby_id, player_id):
            # Update remaining players
            lobby = self.lobby_manager.get_lobby(lobby_id)
            if lobby:
                self._send_lobby_update(lobby_id)
    
    def _handle_player_ready(self, message: NetworkMessage):
        """Handle player ready status"""
        player_id = message.player_id
        data = message.data
        
        lobby_id = data.get('lobby_id')
        ready = data.get('ready', False)
        
        if self.lobby_manager.set_player_ready(lobby_id, player_id, ready):
            lobby = self.lobby_manager.get_lobby(lobby_id)
            if lobby and lobby.state.value == "ready":
                # Start game
                self._start_lobby_game(lobby_id)
            else:
                self._send_lobby_update(lobby_id)
    
    def _handle_spectate_request(self, message: NetworkMessage):
        """Handle spectator request"""
        player_id = message.player_id
        data = message.data
        
        lobby_id = data.get('lobby_id')
        lobby = self.lobby_manager.get_lobby(lobby_id)
        
        if lobby and lobby.state.value == "in_game":
            # Add to spectators
            self.spectators[player_id] = {
                'player_id': player_id,
                'username': f'Spectator_{player_id[:4]}',
                'join_time': time.time()
            }
            
            # Send initial game state to spectator
            self._send_spectator_update(player_id)
    
    def _handle_spectate_stop(self, message: NetworkMessage):
        """Handle spectator stop"""
        player_id = message.player_id
        
        if player_id in self.spectators:
            del self.spectators[player_id]
    
    def _handle_player_input(self, message: NetworkMessage):
        """Handle remote player input"""
        if self.remote_player:
            # Apply input to remote player
            pass
    
    def _handle_game_state(self, message: NetworkMessage):
        """Handle game state update"""
        # Update remote player state
        pass
    
    def _handle_line_clear(self, message: NetworkMessage):
        """Handle line clear effects"""
        self.sound_manager.play_sound('clear')
        
        # Update spectators
        self._update_spectators()
    
    def _handle_chat(self, message: NetworkMessage):
        """Handle game chat"""
        pass
    
    def _handle_lobby_chat(self, message: NetworkMessage):
        """Handle lobby chat"""
        pass
    
    # Helper methods
    def _send_lobby_update(self, lobby_id: str):
        """Send lobby update to all players"""
        lobby = self.lobby_manager.get_lobby(lobby_id)
        if not lobby or not self.network_manager:
            return
        
        # Convert lobby to dict for serialization
        lobby_data = {
            'lobby_id': lobby.lobby_id,
            'name': lobby.name,
            'state': lobby.state.value,
            'players': [
                {
                    'player_id': p.player_id,
                    'username': p.username,
                    'is_ready': p.is_ready,
                    'is_host': p.is_host
                }
                for p in lobby.players.values()
            ],
            'spectators': [
                {
                    'player_id': s.player_id,
                    'username': s.username
                }
                for s in lobby.spectators.values()
            ]
        }
        
        update_msg = NetworkMessage(MessageType.LOBBY_UPDATE, {
            'lobby': lobby_data
        })
        
        # Broadcast to all clients
        if isinstance(self.network_manager, NetworkServer):
            for client_socket in self.network_manager.clients.values():
                # Send to each client (simplified - should use proper broadcasting)
                pass
    
    def _send_spectator_update(self, spectator_id: str):
        """Send game state update to spectator"""
        if not self.local_player or not self.remote_player:
            return
        
        spectator_data = {
            'game_state': 'playing',
            'player1_state': {
                'grid': self.local_player.game.grid,
                'score': self.local_player.game.score,
                'level': self.local_player.game.level,
                'lines_cleared': self.local_player.game.lines_cleared,
                'current_piece': self._get_piece_data(self.local_player.game.current_piece),
                'next_piece': self._get_piece_data(self.local_player.game.next_piece)
            },
            'player2_state': {
                'grid': self.remote_player.game.grid,
                'score': self.remote_player.game.score,
                'level': self.remote_player.game.level,
                'lines_cleared': self.remote_player.game.lines_cleared,
                'current_piece': self._get_piece_data(self.remote_player.game.current_piece),
                'next_piece': self._get_piece_data(self.remote_player.game.next_piece)
            },
            'round_info': {
                'round': self.current_round,
                'max_rounds': self.max_rounds,
                'player1_wins': self.local_wins,
                'player2_wins': self.remote_wins
            },
            'spectators': list(self.spectators.keys())
        }
        
        spectator_msg = NetworkMessage(MessageType.SPECTATE_UPDATE, spectator_data)
        # Send to specific spectator (simplified)
    
    def _get_piece_data(self, piece):
        """Convert piece to serializable data"""
        if not piece:
            return None
        
        return {
            'shape': piece.shape,
            'x': piece.x,
            'y': piece.y,
            'type': piece.type
        }
    
    def _start_lobby_game(self, lobby_id: str):
        """Start game for lobby"""
        if self.lobby_manager.start_game(lobby_id):
            self.mode = "game"
            self.game_state = "playing"
            
            # Initialize players
            self._initialize_game_players()
    
    def _initialize_game_players(self):
        """Initialize game players"""
        self.local_player = NetworkPlayer(
            self.player_id, 
            self.sound_manager, 
            start_level=0,
            is_local=True
        )
        
        self.remote_player = NetworkPlayer(
            "remote", 
            self.sound_manager, 
            start_level=0,
            is_local=False
        )
        
        if self.network_manager:
            self.local_player.set_network_manager(self.network_manager)
            self.remote_player.set_network_manager(self.network_manager)
    
    def _send_game_state_update(self):
        """Send game state update"""
        if not self.local_player or not self.network_manager:
            return
        
        game_data = {
            'player_id': self.player_id,
            'grid': self.local_player.game.grid,
            'score': self.local_player.game.score,
            'level': self.local_player.game.level,
            'lines_cleared': self.local_player.game.lines_cleared,
            'current_piece': self._get_piece_data(self.local_player.game.current_piece),
            'game_over': self.local_player.game.game_over
        }
        
        state_msg = NetworkMessage(MessageType.GAME_STATE, game_data)
        self.network_manager.send_message(state_msg)
    
    def _check_game_end(self):
        """Check for game end conditions"""
        if not self.local_player or not self.remote_player:
            return
        
        local_over = self.local_player.game.game_over
        remote_over = self.remote_player.game.game_over
        
        if local_over or remote_over:
            # Determine round winner
            if local_over and not remote_over:
                self.remote_wins += 1
                self.round_winner = "remote"
            elif remote_over and not local_over:
                self.local_wins += 1
                self.round_winner = "local"
            else:
                # Both game over, check scores
                if self.local_player.game.score > self.remote_player.game.score:
                    self.local_wins += 1
                    self.round_winner = "local"
                else:
                    self.remote_wins += 1
                    self.round_winner = "remote"
            
            self.game_state = "round_end"
            self.round_end_time = time.time()
            
            # Check for match end
            if self.local_wins >= 3 or self.remote_wins >= 3:
                self.game_state = "game_end"
    
    def _update_spectators(self):
        """Update all spectators with current game state"""
        if not self.spectators:
            return
        
        for spectator_id in self.spectators:
            self._send_spectator_update(spectator_id)
    
    def _restart_game(self):
        """Restart game"""
        if self.game_state == "round_end":
            self.current_round += 1
            self._start_next_round()
        elif self.game_state == "game_end":
            self._reset_match()
    
    def _start_next_round(self):
        """Start next round"""
        self.game_state = "playing"
        if self.local_player:
            self.local_player.game.reset()
        if self.remote_player:
            self.remote_player.game.reset()
    
    def _reset_match(self):
        """Reset entire match"""
        self.current_round = 1
        self.local_wins = 0
        self.remote_wins = 0
        self.game_state = "playing"
        if self.local_player:
            self.local_player.game.reset()
        if self.remote_player:
            self.remote_player.game.reset()
    
    def cleanup(self):
        """Cleanup resources"""
        if self.network_manager:
            self.network_manager.disconnect()
        
        if self.spectator_mode.spectating:
            self.spectator_mode.stop_spectating()

def main():
    """Main function for enhanced online battle"""
    game = EnhancedOnlineBattle()
    game.run()

if __name__ == "__main__":
    main()
