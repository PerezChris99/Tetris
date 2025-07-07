# Tetris Battle - Human vs AI

A competitive Tetris game where a human player battles against an AI opponent in a best-of-5 round format.

## Features

- **Split-screen battle**: Human player vs AI on the same screen
- **Best-of-5 rounds**: First to win 3 rounds wins the match
- **Smart AI opponent**: Uses advanced heuristics to make optimal moves
- **Sound effects**: Tetris-style audio feedback
- **Modern UI**: Clean, minimalist design with score tracking
- **Full Tetris mechanics**: All standard tetrominoes, rotations, line clearing, and gravity

## Controls

- **Arrow Keys**: Move pieces (←/→ for left/right, ↓ for soft drop)
- **Up Arrow**: Rotate piece
- **Spacebar**: Hard drop (instant drop)
- **ESC**: Quit game
- **R**: Restart game (on game over screen)
- **M**: Toggle sound on/off

## Installation

1. Make sure you have Python 3.7+ installed
2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the game:
   ```bash
   python main.py
   ```

## Game Rules

- Each round lasts up to 2 minutes
- Round ends when:
  - A player's stack reaches the top (game over)
  - Time runs out (higher score wins)
- First player to win 3 rounds wins the match
- Standard Tetris scoring system applies

## AI Behavior

The AI uses a sophisticated evaluation system based on:
- **Aggregate Height**: Penalty for tall stacks
- **Lines Cleared**: Bonus for clearing lines
- **Holes**: Penalty for creating holes in the grid
- **Bumpiness**: Penalty for uneven surfaces
- **Strategic Depth**: Advanced well and height management

## File Structure

```
tetris_battle/
├── main.py              # Main game loop and UI
├── config.py            # Game configuration and constants
├── game.py              # Core Tetris game engine
├── tetromino.py         # Tetromino shapes and logic
├── player.py            # Human player input handling
├── ai_player.py         # AI decision making
├── sounds.py            # Sound effects management
├── requirements.txt     # Python dependencies
├── assets/
│   ├── sounds/          # Sound effect files
│   └── fonts/           # Font files (optional)
└── README.md           # This file
```

## Sound Effects

The game includes placeholder sound effects. For better audio experience, add your own sound files:

- `move.wav` - Piece movement
- `rotate.wav` - Piece rotation
- `drop.wav` - Hard drop
- `clear.wav` - Line clear
- `gameover.wav` - Game over
- `win.wav` - Round/match win
- `lose.wav` - Round/match loss

Place these files in the `assets/sounds/` directory.

## Customization

You can modify game behavior by editing `config.py`:

- Grid dimensions
- Colors and visual style
- Timing settings
- AI difficulty
- Round settings

## Requirements

- Python 3.7+
- pygame 2.5.0+
- numpy 1.21.0+ (for sound generation)

## Development

The code is organized into modular components:

- **Game Engine** (`game.py`): Core Tetris logic
- **Tetromino System** (`tetromino.py`): Piece generation and rotation
- **Player Input** (`player.py`): Human input with DAS (Delayed Auto Shift)
- **AI Player** (`ai_player.py`): Intelligent opponent with evaluation heuristics
- **Sound System** (`sounds.py`): Audio management with fallback generation
- **Main Loop** (`main.py`): Game state management and rendering

## License

This project is open source and available under the MIT License.

## Credits

Created as a demonstration of advanced Tetris AI and game development techniques.
