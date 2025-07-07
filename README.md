# Tetris Battle - Human vs AI

A competitive Tetris game where a human player battles against an AI opponent in a best-of-5 round format.

## 🎮 What We Built

A complete Tetris Battle game featuring human vs AI gameplay with all requested features:

### ✅ Core Features Implemented

1. **Split-Screen Battle System**
   - Human player on the left side
   - AI opponent on the right side
   - Independent game grids for each player

2. **Complete Tetris Mechanics**
   - All 7 standard tetrominoes (I, O, T, S, Z, J, L)
   - Proper rotation with wall-kick system
   - Line clearing with scoring
   - Gravity system with increasing difficulty
   - Ghost piece preview
   - Lock delay mechanics

3. **Intelligent AI Opponent**
   - Uses advanced heuristics-based evaluation
   - Considers: aggregate height, lines cleared, holes, bumpiness
   - Makes strategic decisions for piece placement
   - Realistic thinking delay to simulate human-like play

4. **Round-Based Competition**
   - Best-of-5 rounds (first to 3 wins)
   - 2-minute time limit per round
   - Multiple win conditions (survival, score, time)
   - Round and match tracking

5. **Sound System**
   - Complete sound effect management
   - Placeholder sound generation when audio files missing
   - Sounds for: move, rotate, drop, line clear, game over, win/lose

6. **Professional UI**
   - Clean, modern interface
   - Real-time score display
   - Round progress tracking
   - Next piece preview
   - Time remaining display
   - Game state overlays

## 🎯 Controls

- **Arrow Keys**: Move and rotate pieces
- **Spacebar**: Hard drop
- **ESC**: Quit game
- **R**: Restart after game end
- **M**: Toggle sound

## 🚀 Installation

1. Make sure you have Python 3.7+ installed
2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the game:
   ```bash
   python main.py
   ```

## 🎮 Game Rules

- Each round lasts up to 2 minutes
- Round ends when:
  - A player's stack reaches the top (game over)
  - Time runs out (higher score wins)
- First player to win 3 rounds wins the match
- Standard Tetris scoring system applies

## 🎯 Game Flow

1. **Round Start**: Both players begin with fresh grids
2. **Gameplay**: Players compete simultaneously
3. **Round End**: Determined by elimination or time/score
4. **Match Progress**: Track wins toward best-of-5
5. **Final Victory**: First to 3 round wins takes the match

## 🤖 AI Features

The AI uses a sophisticated scoring system:
```
score = -0.510066 * aggregate_height +
        0.760666 * lines_cleared +
        -0.35663 * holes +
        -0.184483 * bumpiness
```

Additional considerations:
- Height penalties for dangerous stacks
- Well depth calculations
- Strategic piece placement simulation

The AI evaluation system is based on:
- **Aggregate Height**: Penalty for tall stacks
- **Lines Cleared**: Bonus for clearing lines
- **Holes**: Penalty for creating holes in the grid
- **Bumpiness**: Penalty for uneven surfaces
- **Strategic Depth**: Advanced well and height management

## 📁 Project Structure

```
tetris_battle/
├── main.py              # Game loop & UI
├── config.py            # Constants & settings
├── game.py              # Core Tetris engine
├── tetromino.py         # Piece logic & generation
├── player.py            # Human input handling
├── ai_player.py         # AI decision making
├── sounds.py            # Audio system
├── requirements.txt     # Dependencies
├── README.md           # Documentation
└── assets/
    ├── sounds/          # Sound effect files
    └── fonts/           # Font files
```

## 🎵 Sound System

The game includes a complete sound management system that:
- Loads WAV/OGG audio files when available
- Generates placeholder sounds using numpy when files are missing
- Provides volume control and sound toggling
- Handles audio errors gracefully

For better audio experience, add your own sound files:

- `move.wav` - Piece movement
- `rotate.wav` - Piece rotation
- `drop.wav` - Hard drop
- `clear.wav` - Line clear
- `gameover.wav` - Game over
- `win.wav` - Round/match win
- `lose.wav` - Round/match loss

Place these files in the `assets/sounds/` directory.

## 🎨 Visual Features

- Split-screen layout with clear grid boundaries
- Color-coded tetrominoes
- Ghost piece preview
- Real-time score and statistics
- Round progress indicators
- Game state overlays (round end, game end)
- Clean, minimalist design

## 🔧 Customization Options

The game is highly configurable through `config.py`:
- Grid dimensions and cell size
- Color schemes
- Timing parameters
- AI difficulty settings
- Round and match rules
- UI layout and fonts

You can modify game behavior by editing `config.py`:

- Grid dimensions
- Colors and visual style
- Timing settings
- AI difficulty
- Round settings

## 🚀 Technical Highlights

1. **Advanced Input System**
   - DAS (Delayed Auto Shift) for smooth movement
   - Proper key repeat handling
   - Responsive controls

2. **Robust Game Engine**
   - Collision detection
   - Line clearing algorithm
   - Score calculation
   - Level progression

3. **Smart AI Implementation**
   - Grid state evaluation
   - Move simulation
   - Best move selection
   - Performance optimized

4. **Professional Code Structure**
   - Modular design
   - Clean separation of concerns
   - Extensible architecture
   - Well-documented code

## 📋 Requirements

- Python 3.7+
- pygame 2.5.0+
- numpy 1.21.0+ (for sound generation)

## 🛠️ Development

The code is organized into modular components:

- **Game Engine** (`game.py`): Core Tetris logic
- **Tetromino System** (`tetromino.py`): Piece generation and rotation
- **Player Input** (`player.py`): Human input with DAS (Delayed Auto Shift)
- **AI Player** (`ai_player.py`): Intelligent opponent with evaluation heuristics
- **Sound System** (`sounds.py`): Audio management with fallback generation
- **Main Loop** (`main.py`): Game state management and rendering

## 📄 License

This project is open source and available under the MIT License.

## 🎯 Ready to Play!

The game is fully functional and ready for immediate play. Run with:
```bash
python main.py
```

Experience the thrill of competing against a challenging AI opponent in this polished Tetris Battle implementation!

## 🙏 Credits

Created as a demonstration of advanced Tetris AI and game development techniques.
