# Game Boy Tetris - Authentic Implementation

This implementation aims to recreate the exact experience of the original 1989 Game Boy Tetris with pixel-perfect accuracy.

## Authentic Features Implemented

### 🎮 Controls (Game Boy Authentic)
- **Left/Right**: Move piece horizontally with DAS (Delayed Auto Shift)
- **Up**: Rotate piece counter-clockwise (no wall kicks)
- **Down**: Soft drop (3x faster than normal gravity)
- **No Hard Drop**: Original Game Boy Tetris didn't have hard drop

### 🎯 Gameplay Mechanics
- **Gravity System**: Authentic Game Boy gravity table (frames per row at 59.73 FPS)
- **Level Progression**: Every 10 lines cleared increases level
- **Scoring**: Original BPS (Basic Positioning System) scoring
- **Line Clearing**: 5-frame flash animation with white blocks
- **No Wall Kicks**: Original Game Boy rotation system
- **Spawn Positions**: Exact piece spawn coordinates

### 🎨 Visual Style
- **Monochrome Palette**: 4-shade Game Boy green palette
- **No Ghost Piece**: Original didn't have ghost piece preview (can be enabled)
- **Authentic Grid**: 10x20 grid with 18 visible rows
- **Pixelated Fonts**: Small, authentic Game Boy-style fonts

### 🎵 Audio
- **Game Boy Style Sounds**: Authentic 8-bit sound effects
- **No Background Music**: Original Game Boy Tetris had no BGM during play

### 🔧 Technical Accuracy
- **Piece Randomizer**: Authentic Game Boy pseudo-random algorithm
- **DAS Timing**: 24 frames delay, 10 frames repeat (authentic)
- **Soft Drop**: 1 frame per row (authentic timing)
- **Frame Rate**: 59.73 FPS timing calculations

## Files

### Single Player Mode
- `single_player.py` - Pure Game Boy Tetris experience
- Run with: `python single_player.py`

### Battle Mode
- `main.py` - Human vs AI battle mode
- Run with: `python main.py`

## Authenticity Settings

In `config.py`, you can toggle authenticity features:

```python
# Game Boy authenticity settings
SHOW_GHOST_PIECE = False  # Original had no ghost piece
ENABLE_HARD_DROP = False  # Original had no hard drop
AUTHENTIC_SPAWN_DELAY = True  # Use authentic spawn delays
```

## Controls

### Game Controls
- **Arrow Keys**: Move and rotate pieces
- **ESC**: Quit game
- **R**: Restart (when game over)
- **M**: Toggle sound

### Differences from Modern Tetris
- No hold piece functionality
- No wall kicks on rotation
- No hard drop
- No lock delay (pieces lock immediately)
- No T-spins or advanced techniques

## Scoring System (Authentic BPS)

| Lines Cleared | Base Points |
|---------------|-------------|
| 1 (Single)    | 40          |
| 2 (Double)    | 100         |
| 3 (Triple)    | 300         |
| 4 (Tetris)    | 1200        |

Final score = Base Points × (Level + 1)

## Level Progression

- **Level 0**: 0-9 lines
- **Level 1**: 10-19 lines
- **Level 2**: 20-29 lines
- **...**
- **Level 20**: Maximum level (fastest speed)

## Technical Details

### Gravity Table (frames per row)
Level 0: 53 frames, Level 1: 49 frames, Level 2: 45 frames, etc.

### Piece Spawn Positions
- **I-piece**: Column 3, Row 0
- **O-piece**: Column 4, Row 0
- **T, S, Z, J, L**: Column 3, Row 0

### Line Clearing Animation
- Duration: 5 frames
- Effect: Entire line flashes white
- Pieces freeze during animation

This implementation provides the most authentic Game Boy Tetris experience possible while maintaining modern code quality and structure.
