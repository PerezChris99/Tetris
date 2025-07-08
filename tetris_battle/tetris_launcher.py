#!/usr/bin/env python3
"""
Tetris Battle - Unified Game Launcher
Main entry point for all Tetris game modes

This is the single entry point for:
- Single Player Tetris
- Player vs AI Battle
- Game Boy Classic Tetris
- Online Multiplayer
- Enhanced Online with Lobbies
- Test and Demo Modes

Run this file to access all game modes from one menu.
"""

import sys
import os

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Main entry point for Tetris Battle collection"""
    try:
        # Import and run the main launcher
        from launcher import main as launcher_main
        launcher_main()
    except ImportError as e:
        print(f"Error: Could not import launcher: {e}")
        print("Make sure all required files are in the same directory.")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("=" * 60)
    print("🎮 TETRIS BATTLE - COMPLETE COLLECTION 🎮")
    print("=" * 60)
    print("Available Game Modes:")
    print("• Single Player Tetris")
    print("• Player vs AI Battle")
    print("• Game Boy Classic Tetris")
    print("• Online Multiplayer")
    print("• Enhanced Online with Lobbies & Spectator Mode")
    print("• Test and Demo Modes")
    print("=" * 60)
    print("Starting main menu...")
    print()
    
    main()
