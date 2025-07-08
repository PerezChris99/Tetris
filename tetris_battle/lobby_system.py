"""
Lobby System for Tetris Battle Online Multiplayer
Manages game lobbies, player matchmaking, and room management
"""
import pygame
import time
import threading
import uuid
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
from config import *
from sounds import SoundManager
from network_protocol import NetworkClient, NetworkServer, NetworkMessage, MessageType

# Color definitions for lobby UI
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

class LobbyState(Enum):
    """Lobby states"""
    WAITING = "waiting"
    READY = "ready"
    IN_GAME = "in_game"
    FINISHED = "finished"

@dataclass
class LobbyPlayer:
    """Player information in lobby"""
    player_id: str
    username: str
    is_ready: bool = False
    is_host: bool = False
    is_spectator: bool = False
    join_time: float = 0.0

@dataclass
class GameLobby:
    """Game lobby information"""
    lobby_id: str
    name: str
    host_id: str
    max_players: int = 2
    max_spectators: int = 10
    players: Dict[str, LobbyPlayer] = None
    spectators: Dict[str, LobbyPlayer] = None
    state: LobbyState = LobbyState.WAITING
    created_time: float = 0.0
    game_mode: str = "battle"  # battle, tournament, etc.
    password: str = ""
    
    def __post_init__(self):
        if self.players is None:
            self.players = {}
        if self.spectators is None:
            self.spectators = {}

class LobbyManager:
    """Manages multiple game lobbies"""
    
    def __init__(self):
        self.lobbies: Dict[str, GameLobby] = {}
        self.player_lobby_map: Dict[str, str] = {}  # player_id -> lobby_id
        self.lobby_lock = threading.RLock()
    
    def create_lobby(self, host_id: str, username: str, lobby_name: str, 
                    max_players: int = 2, max_spectators: int = 10, 
                    password: str = "") -> GameLobby:
        """Create a new lobby"""
        with self.lobby_lock:
            lobby_id = str(uuid.uuid4())[:8]
            
            host_player = LobbyPlayer(
                player_id=host_id,
                username=username,
                is_host=True,
                join_time=time.time()
            )
            
            lobby = GameLobby(
                lobby_id=lobby_id,
                name=lobby_name,
                host_id=host_id,
                max_players=max_players,
                max_spectators=max_spectators,
                password=password,
                created_time=time.time()
            )
            
            lobby.players[host_id] = host_player
            self.lobbies[lobby_id] = lobby
            self.player_lobby_map[host_id] = lobby_id
            
            return lobby
    
    def join_lobby(self, lobby_id: str, player_id: str, username: str, 
                  password: str = "", as_spectator: bool = False) -> Optional[GameLobby]:
        """Join an existing lobby"""
        with self.lobby_lock:
            if lobby_id not in self.lobbies:
                return None
            
            lobby = self.lobbies[lobby_id]
            
            # Check password
            if lobby.password and lobby.password != password:
                return None
            
            # Check if player is already in a lobby
            if player_id in self.player_lobby_map:
                old_lobby_id = self.player_lobby_map[player_id]
                self.leave_lobby(old_lobby_id, player_id)
            
            player = LobbyPlayer(
                player_id=player_id,
                username=username,
                is_spectator=as_spectator,
                join_time=time.time()
            )
            
            if as_spectator:
                if len(lobby.spectators) >= lobby.max_spectators:
                    return None
                lobby.spectators[player_id] = player
            else:
                if len(lobby.players) >= lobby.max_players:
                    return None
                lobby.players[player_id] = player
            
            self.player_lobby_map[player_id] = lobby_id
            return lobby
    
    def leave_lobby(self, lobby_id: str, player_id: str) -> bool:
        """Leave a lobby"""
        with self.lobby_lock:
            if lobby_id not in self.lobbies:
                return False
            
            lobby = self.lobbies[lobby_id]
            
            # Remove from players or spectators
            if player_id in lobby.players:
                del lobby.players[player_id]
            elif player_id in lobby.spectators:
                del lobby.spectators[player_id]
            else:
                return False
            
            # Remove from player map
            if player_id in self.player_lobby_map:
                del self.player_lobby_map[player_id]
            
            # If lobby is empty or host left, remove lobby
            if not lobby.players or player_id == lobby.host_id:
                del self.lobbies[lobby_id]
                # Remove all remaining players from map
                for pid in list(lobby.players.keys()) + list(lobby.spectators.keys()):
                    if pid in self.player_lobby_map:
                        del self.player_lobby_map[pid]
            
            return True
    
    def get_lobby_list(self) -> List[Dict[str, Any]]:
        """Get list of available lobbies"""
        with self.lobby_lock:
            lobby_list = []
            for lobby in self.lobbies.values():
                lobby_info = {
                    'lobby_id': lobby.lobby_id,
                    'name': lobby.name,
                    'host_name': lobby.players.get(lobby.host_id, LobbyPlayer("", "")).username,
                    'player_count': len(lobby.players),
                    'max_players': lobby.max_players,
                    'spectator_count': len(lobby.spectators),
                    'max_spectators': lobby.max_spectators,
                    'state': lobby.state.value,
                    'has_password': bool(lobby.password),
                    'game_mode': lobby.game_mode
                }
                lobby_list.append(lobby_info)
            return lobby_list
    
    def get_lobby(self, lobby_id: str) -> Optional[GameLobby]:
        """Get lobby by ID"""
        with self.lobby_lock:
            return self.lobbies.get(lobby_id)
    
    def get_player_lobby(self, player_id: str) -> Optional[GameLobby]:
        """Get lobby that player is in"""
        with self.lobby_lock:
            lobby_id = self.player_lobby_map.get(player_id)
            if lobby_id:
                return self.lobbies.get(lobby_id)
            return None
    
    def set_player_ready(self, lobby_id: str, player_id: str, ready: bool) -> bool:
        """Set player ready status"""
        with self.lobby_lock:
            lobby = self.lobbies.get(lobby_id)
            if not lobby or player_id not in lobby.players:
                return False
            
            lobby.players[player_id].is_ready = ready
            
            # Check if all players are ready
            all_ready = all(player.is_ready for player in lobby.players.values())
            if all_ready and len(lobby.players) >= 2:
                lobby.state = LobbyState.READY
            else:
                lobby.state = LobbyState.WAITING
            
            return True
    
    def start_game(self, lobby_id: str) -> bool:
        """Start game in lobby"""
        with self.lobby_lock:
            lobby = self.lobbies.get(lobby_id)
            if not lobby or lobby.state != LobbyState.READY:
                return False
            
            lobby.state = LobbyState.IN_GAME
            return True

class LobbyUI:
    """UI for lobby system"""
    
    def __init__(self, screen: pygame.Surface, sound_manager: SoundManager):
        self.screen = screen
        self.sound_manager = sound_manager
        
        # Fonts
        self.font_large = pygame.font.Font(None, FONT_LARGE)
        self.font_medium = pygame.font.Font(None, FONT_MEDIUM)
        self.font_small = pygame.font.Font(None, FONT_SMALL)
        
        # UI state
        self.state = "lobby_list"  # lobby_list, lobby_room, create_lobby
        self.lobby_list = []
        self.selected_lobby = 0
        self.current_lobby = None
        self.chat_messages = []
        self.chat_input = ""
        self.chat_active = False
        
        # Create lobby inputs
        self.create_inputs = {
            'name': '',
            'password': '',
            'max_players': '2',
            'max_spectators': '10'
        }
        self.create_field_selected = 0
        self.create_fields = list(self.create_inputs.keys())
        
        # Network
        self.network_manager = None
        self.player_id = str(uuid.uuid4())[:8]
        self.username = f"Player_{self.player_id}"
    
    def set_network_manager(self, network_manager):
        """Set network manager"""
        self.network_manager = network_manager
        if network_manager:
            network_manager.register_handler(MessageType.LOBBY_LIST, self._handle_lobby_list)
            network_manager.register_handler(MessageType.LOBBY_UPDATE, self._handle_lobby_update)
            network_manager.register_handler(MessageType.LOBBY_CHAT, self._handle_lobby_chat)
            network_manager.register_handler(MessageType.ERROR, self._handle_error)
    
    def handle_input(self, event):
        """Handle input events"""
        if self.state == "lobby_list":
            self._handle_lobby_list_input(event)
        elif self.state == "lobby_room":
            self._handle_lobby_room_input(event)
        elif self.state == "create_lobby":
            self._handle_create_lobby_input(event)
    
    def _handle_lobby_list_input(self, event):
        """Handle lobby list input"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_lobby = max(0, self.selected_lobby - 1)
            elif event.key == pygame.K_DOWN:
                self.selected_lobby = min(len(self.lobby_list) - 1, self.selected_lobby + 1)
            elif event.key == pygame.K_RETURN:
                if self.lobby_list:
                    self._join_selected_lobby()
            elif event.key == pygame.K_c:
                self.state = "create_lobby"
            elif event.key == pygame.K_r:
                self._refresh_lobby_list()
    
    def _handle_lobby_room_input(self, event):
        """Handle lobby room input"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._leave_lobby()
            elif event.key == pygame.K_r and not self.chat_active:
                self._toggle_ready()
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
    
    def _handle_create_lobby_input(self, event):
        """Handle create lobby input"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state = "lobby_list"
            elif event.key == pygame.K_UP:
                self.create_field_selected = max(0, self.create_field_selected - 1)
            elif event.key == pygame.K_DOWN:
                self.create_field_selected = min(len(self.create_fields) - 1, self.create_field_selected + 1)
            elif event.key == pygame.K_RETURN:
                self._create_lobby()
            elif event.key == pygame.K_BACKSPACE:
                field = self.create_fields[self.create_field_selected]
                self.create_inputs[field] = self.create_inputs[field][:-1]
            elif event.unicode.isprintable():
                field = self.create_fields[self.create_field_selected]
                if len(self.create_inputs[field]) < 30:
                    self.create_inputs[field] += event.unicode
    
    def draw(self):
        """Draw lobby UI"""
        self.screen.fill(BLACK)
        
        if self.state == "lobby_list":
            self._draw_lobby_list()
        elif self.state == "lobby_room":
            self._draw_lobby_room()
        elif self.state == "create_lobby":
            self._draw_create_lobby()
    
    def _draw_lobby_list(self):
        """Draw lobby list"""
        # Title
        title = self.font_large.render("TETRIS BATTLE - LOBBY", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.screen.blit(title, title_rect)
        
        # Instructions
        instructions = [
            "↑↓ Navigate  ENTER Join  C Create  R Refresh  ESC Back",
            f"Lobbies ({len(self.lobby_list)})"
        ]
        
        y = 100
        for instruction in instructions:
            text = self.font_small.render(instruction, True, GRAY)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
            self.screen.blit(text, text_rect)
            y += 30
        
        # Lobby list
        start_y = 170
        for i, lobby in enumerate(self.lobby_list):
            color = YELLOW if i == self.selected_lobby else WHITE
            
            # Lobby info
            name = lobby['name'][:25]  # Truncate long names
            players = f"{lobby['player_count']}/{lobby['max_players']}"
            spectators = f"👥{lobby['spectator_count']}"
            status = lobby['state'].upper()
            lock = "🔒" if lobby['has_password'] else ""
            
            lobby_text = f"{name} | {players} | {spectators} | {status} {lock}"
            text = self.font_medium.render(lobby_text, True, color)
            
            y_pos = start_y + i * 35
            if y_pos < SCREEN_HEIGHT - 50:  # Don't draw outside screen
                self.screen.blit(text, (50, y_pos))
        
        # No lobbies message
        if not self.lobby_list:
            no_lobbies = self.font_medium.render("No lobbies available. Press C to create one.", True, GRAY)
            no_lobbies_rect = no_lobbies.get_rect(center=(SCREEN_WIDTH // 2, 250))
            self.screen.blit(no_lobbies, no_lobbies_rect)
    
    def _draw_lobby_room(self):
        """Draw lobby room"""
        if not self.current_lobby:
            return
        
        # Title
        title = f"LOBBY: {self.current_lobby['name']}"
        title_text = self.font_large.render(title, True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 30))
        self.screen.blit(title_text, title_rect)
        
        # Players section
        y = 80
        players_title = self.font_medium.render("PLAYERS:", True, WHITE)
        self.screen.blit(players_title, (50, y))
        y += 40
        
        for player in self.current_lobby.get('players', []):
            ready_status = "✓" if player['is_ready'] else "✗"
            host_status = "👑" if player['is_host'] else ""
            player_text = f"{ready_status} {host_status} {player['username']}"
            color = GREEN if player['is_ready'] else RED
            
            text = self.font_small.render(player_text, True, color)
            self.screen.blit(text, (70, y))
            y += 25
        
        # Spectators section
        if self.current_lobby.get('spectators'):
            y += 20
            spectators_title = self.font_medium.render("SPECTATORS:", True, WHITE)
            self.screen.blit(spectators_title, (50, y))
            y += 30
            
            for spectator in self.current_lobby['spectators']:
                spectator_text = f"👁 {spectator['username']}"
                text = self.font_small.render(spectator_text, True, GRAY)
                self.screen.blit(text, (70, y))
                y += 25
        
        # Chat section
        chat_y = SCREEN_HEIGHT - 200
        chat_title = self.font_medium.render("CHAT:", True, WHITE)
        self.screen.blit(chat_title, (50, chat_y))
        chat_y += 30
        
        # Chat messages
        for message in self.chat_messages[-5:]:  # Show last 5 messages
            chat_text = f"{message['username']}: {message['text']}"
            text = self.font_small.render(chat_text[:80], True, WHITE)  # Truncate long messages
            self.screen.blit(text, (70, chat_y))
            chat_y += 20
        
        # Chat input
        if self.chat_active:
            input_text = f"> {self.chat_input}|"
            color = YELLOW
        else:
            input_text = "Press ENTER to chat"
            color = GRAY
        
        chat_input_text = self.font_small.render(input_text, True, color)
        self.screen.blit(chat_input_text, (70, SCREEN_HEIGHT - 60))
        
        # Instructions
        instructions = "R Ready  ENTER Chat  ESC Leave"
        instr_text = self.font_small.render(instructions, True, GRAY)
        instr_rect = instr_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
        self.screen.blit(instr_text, instr_rect)
    
    def _draw_create_lobby(self):
        """Draw create lobby screen"""
        # Title
        title = self.font_large.render("CREATE LOBBY", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.screen.blit(title, title_rect)
        
        # Input fields
        y = 150
        field_labels = {
            'name': 'Lobby Name:',
            'password': 'Password (optional):',
            'max_players': 'Max Players:',
            'max_spectators': 'Max Spectators:'
        }
        
        for i, field in enumerate(self.create_fields):
            color = YELLOW if i == self.create_field_selected else WHITE
            
            label = field_labels[field]
            label_text = self.font_medium.render(label, True, color)
            self.screen.blit(label_text, (100, y))
            
            value = self.create_inputs[field]
            if field == 'password' and value:
                value = '*' * len(value)  # Hide password
            
            value_text = self.font_medium.render(value + ('|' if i == self.create_field_selected else ''), True, color)
            self.screen.blit(value_text, (300, y))
            
            y += 50
        
        # Instructions
        instructions = "↑↓ Navigate  ENTER Create  ESC Back"
        instr_text = self.font_small.render(instructions, True, GRAY)
        instr_rect = instr_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        self.screen.blit(instr_text, instr_rect)
    
    # Network message handlers
    def _handle_lobby_list(self, message: NetworkMessage):
        """Handle lobby list update"""
        self.lobby_list = message.data.get('lobbies', [])
        self.selected_lobby = min(self.selected_lobby, len(self.lobby_list) - 1)
    
    def _handle_lobby_update(self, message: NetworkMessage):
        """Handle lobby update"""
        self.current_lobby = message.data.get('lobby')
    
    def _handle_lobby_chat(self, message: NetworkMessage):
        """Handle lobby chat message"""
        self.chat_messages.append(message.data)
        if len(self.chat_messages) > 50:  # Keep only recent messages
            self.chat_messages = self.chat_messages[-50:]
    
    def _handle_error(self, message: NetworkMessage):
        """Handle error message"""
        print(f"Lobby error: {message.data.get('message', 'Unknown error')}")
    
    # UI actions
    def _refresh_lobby_list(self):
        """Request lobby list refresh"""
        if self.network_manager:
            msg = NetworkMessage(MessageType.LOBBY_LIST, {})
            self.network_manager.send_message(msg)
    
    def _join_selected_lobby(self):
        """Join the selected lobby"""
        if self.network_manager and self.lobby_list:
            lobby = self.lobby_list[self.selected_lobby]
            msg = NetworkMessage(MessageType.LOBBY_JOIN, {
                'lobby_id': lobby['lobby_id'],
                'username': self.username,
                'password': '',  # TODO: Add password input
                'as_spectator': False
            })
            self.network_manager.send_message(msg)
            self.state = "lobby_room"
    
    def _leave_lobby(self):
        """Leave current lobby"""
        if self.network_manager and self.current_lobby:
            msg = NetworkMessage(MessageType.LOBBY_LEAVE, {
                'lobby_id': self.current_lobby['lobby_id']
            })
            self.network_manager.send_message(msg)
            self.state = "lobby_list"
            self.current_lobby = None
    
    def _toggle_ready(self):
        """Toggle ready status"""
        if self.network_manager and self.current_lobby:
            # Find current player's ready status
            current_ready = False
            for player in self.current_lobby.get('players', []):
                if player['player_id'] == self.player_id:
                    current_ready = player['is_ready']
                    break
            
            msg = NetworkMessage(MessageType.READY, {
                'lobby_id': self.current_lobby['lobby_id'],
                'ready': not current_ready
            })
            self.network_manager.send_message(msg)
    
    def _send_chat_message(self):
        """Send chat message"""
        if self.network_manager and self.chat_input.strip():
            msg = NetworkMessage(MessageType.LOBBY_CHAT, {
                'lobby_id': self.current_lobby['lobby_id'] if self.current_lobby else None,
                'username': self.username,
                'text': self.chat_input.strip()
            })
            self.network_manager.send_message(msg)
    
    def _create_lobby(self):
        """Create new lobby"""
        if self.network_manager:
            try:
                max_players = int(self.create_inputs['max_players']) if self.create_inputs['max_players'] else 2
                max_spectators = int(self.create_inputs['max_spectators']) if self.create_inputs['max_spectators'] else 10
            except ValueError:
                max_players = 2
                max_spectators = 10
            
            msg = NetworkMessage(MessageType.LOBBY_CREATE, {
                'name': self.create_inputs['name'] or f"{self.username}'s Lobby",
                'username': self.username,
                'max_players': max_players,
                'max_spectators': max_spectators,
                'password': self.create_inputs['password']
            })
            self.network_manager.send_message(msg)
            self.state = "lobby_room"
