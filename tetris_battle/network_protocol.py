"""
Network Protocol for Tetris Battle Online Multiplayer
Handles all network communication between players
"""
import json
import socket
import threading
import time
import select
from enum import Enum
from typing import Dict, Any, Optional, Callable

class MessageType(Enum):
    """Network message types"""
    # Connection messages
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    PING = "ping"
    PONG = "pong"
    
    # Game state messages
    GAME_STATE = "game_state"
    PLAYER_INPUT = "player_input"
    PIECE_DROP = "piece_drop"
    LINE_CLEAR = "line_clear"
    GARBAGE_SEND = "garbage_send"
    
    # Match control messages
    READY = "ready"
    START_ROUND = "start_round"
    END_ROUND = "end_round"
    GAME_OVER = "game_over"
    
    # Lobby system messages
    LOBBY_CREATE = "lobby_create"
    LOBBY_JOIN = "lobby_join"
    LOBBY_LEAVE = "lobby_leave"
    LOBBY_LIST = "lobby_list"
    LOBBY_UPDATE = "lobby_update"
    LOBBY_PLAYER_LIST = "lobby_player_list"
    
    # Spectator messages
    SPECTATE_REQUEST = "spectate_request"
    SPECTATE_START = "spectate_start"
    SPECTATE_STOP = "spectate_stop"
    SPECTATE_UPDATE = "spectate_update"
    
    # Chat messages
    CHAT = "chat"
    LOBBY_CHAT = "lobby_chat"
    
    # Error messages
    ERROR = "error"

class NetworkMessage:
    """Network message structure"""
    def __init__(self, msg_type: MessageType, data: Dict[str, Any], player_id: str = None):
        self.type = msg_type
        self.data = data
        self.player_id = player_id
        self.timestamp = time.time()
    
    def to_json(self) -> str:
        """Convert message to JSON string"""
        return json.dumps({
            'type': self.type.value,
            'data': self.data,
            'player_id': self.player_id,
            'timestamp': self.timestamp
        })
    
    @classmethod
    def from_json(cls, json_str: str) -> 'NetworkMessage':
        """Create message from JSON string"""
        try:
            data = json.loads(json_str)
            return cls(
                MessageType(data['type']),
                data['data'],
                data.get('player_id'),
            )
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise ValueError(f"Invalid message format: {e}")

class NetworkManager:
    """Base network manager class"""
    def __init__(self, player_id: str):
        self.player_id = player_id
        self.socket = None
        self.connected = False
        self.running = False
        self.message_handlers: Dict[MessageType, Callable] = {}
        self.receive_thread = None
        self.ping_thread = None
        self.last_ping_time = 0
        self.ping_interval = 30  # seconds
        
    def register_handler(self, message_type: MessageType, handler: Callable):
        """Register a message handler"""
        self.message_handlers[message_type] = handler
    
    def send_message(self, message: NetworkMessage) -> bool:
        """Send a message over the network"""
        if not self.connected or not self.socket:
            return False
        
        try:
            message.player_id = self.player_id
            data = message.to_json().encode('utf-8')
            length = len(data)
            
            # Send length first, then data
            self.socket.sendall(length.to_bytes(4, byteorder='big'))
            self.socket.sendall(data)
            return True
        except Exception as e:
            print(f"Error sending message: {e}")
            self.disconnect()
            return False
    
    def _receive_messages(self):
        """Receive messages in a separate thread"""
        while self.running and self.connected:
            try:
                # Check if socket has data to read
                ready = select.select([self.socket], [], [], 0.1)
                if not ready[0]:
                    continue
                
                # Receive length
                length_data = self._receive_exact(4)
                if not length_data:
                    break
                
                length = int.from_bytes(length_data, byteorder='big')
                
                # Receive message data
                message_data = self._receive_exact(length)
                if not message_data:
                    break
                
                # Parse and handle message
                try:
                    message = NetworkMessage.from_json(message_data.decode('utf-8'))
                    self._handle_message(message)
                except ValueError as e:
                    print(f"Invalid message received: {e}")
                    
            except Exception as e:
                print(f"Error receiving message: {e}")
                break
        
        self.disconnect()
    
    def _receive_exact(self, length: int) -> Optional[bytes]:
        """Receive exact number of bytes"""
        data = b''
        while len(data) < length:
            try:
                chunk = self.socket.recv(length - len(data))
                if not chunk:
                    return None
                data += chunk
            except Exception:
                return None
        return data
    
    def _handle_message(self, message: NetworkMessage):
        """Handle received message"""
        handler = self.message_handlers.get(message.type)
        if handler:
            try:
                handler(message)
            except Exception as e:
                print(f"Error handling message {message.type}: {e}")
        else:
            print(f"No handler for message type: {message.type}")
    
    def _ping_loop(self):
        """Send periodic ping messages"""
        while self.running and self.connected:
            time.sleep(self.ping_interval)
            if self.connected:
                ping_msg = NetworkMessage(MessageType.PING, {})
                self.send_message(ping_msg)
    
    def disconnect(self):
        """Disconnect from network"""
        self.running = False
        self.connected = False
        
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
        
        if self.receive_thread and self.receive_thread.is_alive():
            self.receive_thread.join(timeout=1)
        
        if self.ping_thread and self.ping_thread.is_alive():
            self.ping_thread.join(timeout=1)

class NetworkClient(NetworkManager):
    """Network client for connecting to server"""
    def __init__(self, player_id: str):
        super().__init__(player_id)
        self.server_address = None
    
    def connect(self, host: str, port: int) -> bool:
        """Connect to server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)  # 10 second timeout
            self.socket.connect((host, port))
            self.socket.settimeout(None)  # Remove timeout after connection
            
            self.connected = True
            self.running = True
            self.server_address = (host, port)
            
            # Start receive thread
            self.receive_thread = threading.Thread(target=self._receive_messages, daemon=True)
            self.receive_thread.start()
            
            # Start ping thread
            self.ping_thread = threading.Thread(target=self._ping_loop, daemon=True)
            self.ping_thread.start()
            
            # Send connection message
            connect_msg = NetworkMessage(MessageType.CONNECT, {'player_id': self.player_id})
            self.send_message(connect_msg)
            
            return True
            
        except Exception as e:
            print(f"Failed to connect to server: {e}")
            self.disconnect()
            return False

class NetworkServer(NetworkManager):
    """Network server for hosting games"""
    def __init__(self, player_id: str):
        super().__init__(player_id)
        self.server_socket = None
        self.clients = {}  # player_id -> socket
        self.client_threads = {}
        self.accept_thread = None
        self.port = None
    
    def start_server(self, port: int = 0) -> Optional[int]:
        """Start server on specified port (0 for random available port)"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('', port))
            self.server_socket.listen(1)  # Only allow 1 connection for 1v1
            
            self.port = self.server_socket.getsockname()[1]
            self.running = True
            
            # Start accept thread
            self.accept_thread = threading.Thread(target=self._accept_connections, daemon=True)
            self.accept_thread.start()
            
            print(f"Server started on port {self.port}")
            return self.port
            
        except Exception as e:
            print(f"Failed to start server: {e}")
            self.stop_server()
            return None
    
    def _accept_connections(self):
        """Accept incoming connections"""
        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                print(f"Client connected from {address}")
                
                # Handle client in separate thread
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, address),
                    daemon=True
                )
                client_thread.start()
                
            except Exception as e:
                if self.running:
                    print(f"Error accepting connection: {e}")
                break
    
    def _handle_client(self, client_socket: socket.socket, address):
        """Handle individual client connection"""
        client_id = None
        
        try:
            while self.running:
                # Check if socket has data
                ready = select.select([client_socket], [], [], 0.1)
                if not ready[0]:
                    continue
                
                # Receive length
                length_data = self._receive_exact_from_socket(client_socket, 4)
                if not length_data:
                    break
                
                length = int.from_bytes(length_data, byteorder='big')
                
                # Receive message
                message_data = self._receive_exact_from_socket(client_socket, length)
                if not message_data:
                    break
                
                # Parse message
                try:
                    message = NetworkMessage.from_json(message_data.decode('utf-8'))
                    
                    # Handle connection message
                    if message.type == MessageType.CONNECT:
                        client_id = message.data.get('player_id')
                        if client_id:
                            self.clients[client_id] = client_socket
                            print(f"Player {client_id} connected")
                    
                    # Broadcast message to other clients
                    self._broadcast_message(message, exclude=client_id)
                    
                    # Handle message locally
                    self._handle_message(message)
                    
                except ValueError as e:
                    print(f"Invalid message from client: {e}")
                    
        except Exception as e:
            print(f"Error handling client {address}: {e}")
        finally:
            # Cleanup client
            if client_id and client_id in self.clients:
                del self.clients[client_id]
                print(f"Player {client_id} disconnected")
            
            try:
                client_socket.close()
            except:
                pass
    
    def _receive_exact_from_socket(self, sock: socket.socket, length: int) -> Optional[bytes]:
        """Receive exact number of bytes from specific socket"""
        data = b''
        while len(data) < length:
            try:
                chunk = sock.recv(length - len(data))
                if not chunk:
                    return None
                data += chunk
            except Exception:
                return None
        return data
    
    def _broadcast_message(self, message: NetworkMessage, exclude: str = None):
        """Broadcast message to all connected clients"""
        disconnected = []
        
        for client_id, client_socket in self.clients.items():
            if client_id == exclude:
                continue
            
            try:
                data = message.to_json().encode('utf-8')
                length = len(data)
                
                client_socket.sendall(length.to_bytes(4, byteorder='big'))
                client_socket.sendall(data)
                
            except Exception as e:
                print(f"Error broadcasting to {client_id}: {e}")
                disconnected.append(client_id)
        
        # Remove disconnected clients
        for client_id in disconnected:
            if client_id in self.clients:
                del self.clients[client_id]
    
    def stop_server(self):
        """Stop server"""
        self.running = False
        
        # Close all client connections
        for client_socket in self.clients.values():
            try:
                client_socket.close()
            except:
                pass
        self.clients.clear()
        
        # Close server socket
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
            self.server_socket = None
        
        # Wait for threads to finish
        if self.accept_thread and self.accept_thread.is_alive():
            self.accept_thread.join(timeout=1)
        
        for thread in self.client_threads.values():
            if thread.is_alive():
                thread.join(timeout=1)
