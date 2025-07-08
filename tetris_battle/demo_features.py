"""
Demo script for Lobby System and Spectator Mode
Shows the new features in action
"""
import pygame
import time
import sys
from lobby_system import LobbyManager, LobbyUI
from spectator_mode import SpectatorMode
from sounds import SoundManager
from config import *

def demo_lobby_system():
    """Demo the lobby system functionality"""
    print("=== Tetris Battle - Lobby System Demo ===\n")
    
    # Initialize lobby manager
    lobby_manager = LobbyManager()
    
    # Demo: Create a lobby
    print("1. Creating a lobby...")
    lobby = lobby_manager.create_lobby(
        host_id="demo_host",
        username="DemoHost",
        lobby_name="Demo Battle Room",
        max_players=2,
        max_spectators=5
    )
    print(f"   ✓ Created lobby: {lobby.name} (ID: {lobby.lobby_id})")
    
    # Demo: Join as player
    print("\n2. Player joining lobby...")
    joined_lobby = lobby_manager.join_lobby(
        lobby_id=lobby.lobby_id,
        player_id="demo_player",
        username="DemoPlayer"
    )
    print(f"   ✓ Player joined successfully")
    
    # Demo: Join as spectator
    print("\n3. Spectator joining...")
    spectator_lobby = lobby_manager.join_lobby(
        lobby_id=lobby.lobby_id,
        player_id="demo_spectator",
        username="DemoSpectator",
        as_spectator=True
    )
    print(f"   ✓ Spectator joined successfully")
    
    # Demo: Set players ready
    print("\n4. Setting players ready...")
    lobby_manager.set_player_ready(lobby.lobby_id, "demo_host", True)
    lobby_manager.set_player_ready(lobby.lobby_id, "demo_player", True)
    
    updated_lobby = lobby_manager.get_lobby(lobby.lobby_id)
    print(f"   ✓ Lobby state: {updated_lobby.state.value}")
    
    # Demo: Get lobby list
    print("\n5. Lobby list:")
    lobby_list = lobby_manager.get_lobby_list()
    for lobby_info in lobby_list:
        print(f"   - {lobby_info['name']}: {lobby_info['player_count']}/{lobby_info['max_players']} players, "
              f"{lobby_info['spectator_count']} spectators")
    
    print("\n=== Lobby Demo Complete ===")

def demo_spectator_ui():
    """Demo the spectator mode UI"""
    print("\n=== Spectator Mode Demo ===")
    
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Tetris Battle - Spectator Demo")
    
    sound_manager = SoundManager()
    spectator = SpectatorMode(screen, sound_manager)
    
    # Set up demo data
    spectator.spectating = True
    spectator.player1_state = {
        'grid': [[0 if (i + j) % 3 != 0 else 1 for j in range(GRID_WIDTH)] for i in range(GRID_HEIGHT)],
        'score': 15000,
        'level': 5,
        'lines_cleared': 23,
        'current_piece': {
            'shape': [[1, 1, 1], [0, 1, 0]],
            'x': 4,
            'y': 2,
            'type': 3
        },
        'next_piece': {
            'shape': [[1, 1], [1, 1]],
            'type': 2
        }
    }
    
    spectator.player2_state = {
        'grid': [[0 if (i + j) % 4 != 0 else 2 for j in range(GRID_WIDTH)] for i in range(GRID_HEIGHT)],
        'score': 12500,
        'level': 4,
        'lines_cleared': 19,
        'current_piece': {
            'shape': [[1, 1, 1, 1]],
            'x': 3,
            'y': 1,
            'type': 1
        },
        'next_piece': {
            'shape': [[1, 1, 1], [1, 0, 0]],
            'type': 6
        }
    }
    
    spectator.round_info = {
        'round': 3,
        'max_rounds': 5,
        'player1_wins': 2,
        'player2_wins': 1
    }
    
    spectator.spectator_list = ['spec1', 'spec2', 'spec3']
    spectator.chat_messages = [
        {'username': 'Viewer1', 'text': 'Great match!'},
        {'username': 'Viewer2', 'text': 'Player 1 is doing well'},
        {'username': 'Viewer3', 'text': 'Nice Tetris!'}
    ]
    
    print("   ✓ Spectator mode initialized with demo data")
    print("   ✓ Controls: ESC=Exit, C=Chat, S=Stats, N=Next, 1/2/A=Camera")
    print("   ✓ Press ESC in the spectator window to close demo")
    
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
    print("   ✓ Spectator demo completed")

def main():
    """Run full demo"""
    print("Tetris Battle - Enhanced Features Demo")
    print("=====================================\n")
    
    # Demo lobby system
    demo_lobby_system()
    
    # Ask if user wants to see spectator demo
    print(f"\nWould you like to see the spectator mode demo? (y/n): ", end="")
    response = input().lower().strip()
    
    if response in ['y', 'yes']:
        demo_spectator_ui()
    
    print("\n🎮 Demo completed!")
    print("\nTo try the full experience:")
    print("1. Run: python launcher.py")
    print("2. Select 'Enhanced Online (Lobby + Spectator)'")
    print("3. Create or join lobbies to play with friends!")

if __name__ == "__main__":
    main()
