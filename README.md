# 🎮 Tetris Battle - Complete Collection

## 🚀 Quick Start

**One entry point for all game modes:**

```bash
# Windows
START_TETRIS.bat

# Or run directly
python tetris_launcher.py
```

## 🎮 Game Modes

### 1. **Single Player**
Classic Tetris experience:
- Authentic Game Boy Tetris feel
- Progressive difficulty levels
- Score and line tracking

### 2. **Player vs AI Battle**
Battle against an intelligent AI opponent in split-screen mode:
- Advanced heuristics-based AI
- Best-of-5 round competition  
- Real-time statistics and graphs

### 3. **Game Boy Tetris (Classic)**
Authentic 1989 Game Boy Tetris experience:
- Original gravity system and mechanics
- Nostalgic monochrome graphics
- Classic scoring system

### 4. **Online Multiplayer** 🆕
Battle other human players over the internet:
- Host or join games easily
- Real-time synchronized gameplay
- Garbage line attack system
- Works on local networks and internet

### 5. **Enhanced Online (Lobby + Spectator)** 🆕
Advanced multiplayer with full lobby system:
- **Create & Browse Lobbies** with chat and ready system
- **Spectator Mode** to watch ongoing battles
- **Password Protection** for private games
- **Multi-game Support** for tournaments
- **Real-time Statistics** and viewer management

### 6. **Test & Demo Modes**
Comprehensive testing and demonstration:
- AI performance testing
- Network connectivity tests
- System diagnostics
- Sound and graphics validation

## 🌟 New Feature: Enhanced Online Multiplayer!

**Now you can battle other players over the internet in real-time with advanced features!**

- 🌐 **Real-time network synchronization**
- 🎯 **Cross-platform compatibility** (Windows, Mac, Linux)  
- ⚡ **Low-latency gameplay** optimized for responsive controls
- 🏆 **Competitive attack system** with garbage lines
- 🔒 **Secure TCP connections** with automatic reconnection
- 📡 **LAN and Internet play** support

### 🏛️ **NEW: Lobby System**
- **Create & Browse Lobbies** - Host your own games or join existing ones
- **Real-time Chat** - Communicate with players before and during games
- **Ready System** - Ensure all players are prepared before starting
- **Password Protection** - Private lobbies for friends
- **Player Management** - See who's in the lobby and their status

### 👁️ **NEW: Spectator Mode**
- **Watch Live Games** - Observe ongoing battles in real-time
- **Multiple Camera Modes** - Follow specific players or auto-switching
- **Spectator Chat** - Discuss the game with other viewers
- **Game Statistics** - See scores, levels, and round progress
- **No Lag Viewing** - Optimized for smooth spectating experience

## 🎮 Game Modes

### 1. **Local Battle (vs AI)**
Battle against an intelligent AI opponent in split-screen mode:
- Advanced heuristics-based AI
- Best-of-5 round competition  
- Real-time statistics and graphs

### 2. **Online Multiplayer** �
Battle other human players over the internet:
- Host or join games easily
- Real-time synchronized gameplay
- Garbage line attack system
- Works on local networks and internet

### 3. **Single Player**
Classic Tetris experience:
- Authentic Game Boy Tetris feel
- Progressive difficulty levels
- Score and line tracking

## 🚀 Quick Start

### Local Battle
```bash
python launcher.py
# Select "Local Battle (vs AI)"
```

### Online Multiplayer
```bash
python launcher.py  
# Select "Online Multiplayer"
# Choose "Host Game" or "Join Game"
```

### Network Setup Test
```bash
python network_test.py test
```

## 🎯 Core Features

### ✅ Local Battle Features

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
   - Multiple win conditions (survival, score, lines)
   - Round and match tracking

### ✅ Online Multiplayer Features 🆕

1. **Real-Time Network Play**
   - TCP-based reliable connection
   - Low-latency input synchronization
   - Automatic state synchronization
   - Connection health monitoring

2. **Easy Connection Setup**
   - Host/Join game interface
   - Automatic IP detection
   - Built-in network testing
   - Clear connection instructions

3. **Competitive Attack System**
   - Send garbage lines when clearing multiple lines
   - 2 lines = 1 garbage, 3 lines = 2 garbage, 4 lines = 4 garbage
   - Strategic timing for maximum impact

4. **Cross-Network Support**
   - Local network (LAN/WiFi) play
   - Internet play with port forwarding
   - VPN compatibility for easy setup

### ✅ Shared Features

5. **Sound System**
   - Complete sound effect management
   - Placeholder sound generation when audio files missing
   - Sounds for: move, rotate, drop, line clear, game over, win/lose

6. **Professional UI**
   - Clean, modern interface
   - Real-time score display
   - Round progress tracking
   - Next piece preview
   - Game state overlays

## 🎯 Controls

### Local Battle & Single Player
- **Arrow Keys**: Move and rotate pieces
- **Spacebar**: Hard drop
- **ESC**: Quit game
- **R**: Restart after game end
- **M**: Toggle sound

### Online Multiplayer
- **Arrow Keys**: Move and rotate pieces (synchronized with opponent)
- **Spacebar**: Hard drop
- **Down Arrow**: Soft drop
- **M**: Toggle sound
- **R**: Restart game (when ended)
- **ESC**: Return to menu

## 🚀 Installation & Setup

### Basic Installation
1. Make sure you have Python 3.7+ installed
2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

### Quick Start
```bash
# Launch main menu with all game modes
python launcher.py
```

### Individual Game Modes
```bash
# Local battle vs AI
python main.py

# Online multiplayer  
python online_battle.py

# Single player
python single_player.py
```

### Network Testing
```bash
# Test your network setup for online play
python network_test.py test

# Get your local IP address
python network_test.py ip

# Test connection to specific host
python network_test.py check <host> <port>
```

## 🌐 Online Multiplayer Setup

### Quick Setup (Same WiFi/LAN)
1. Both players should be on the same network
2. Host runs: `python launcher.py` → "Online Multiplayer" → "Host Game"
3. Joiner runs: `python launcher.py` → "Online Multiplayer" → "Join Game"
4. Joiner enters host's IP address and port number

### Internet Play Setup
1. **Host configures port forwarding** on their router (forward the game port to their computer)
2. **Host shares their public IP** (find at whatismyip.com) and port
3. **Joiner connects** using the public IP and port

### Easy Setup with VPN
1. Both players install a VPN service (Hamachi, ZeroTier, etc.)
2. Join the same VPN network
3. Use VPN IP addresses to connect

📖 **For detailed setup instructions, see [ONLINE_MULTIPLAYER.md](tetris_battle/ONLINE_MULTIPLAYER.md)**

## 🎮 Game Rules

### Local Battle (vs AI)
- Each round lasts up to 2 minutes
- Round ends when:
  - A player's stack reaches the top (game over)
  - Time runs out (higher score wins)
- First player to win 3 rounds wins the match
- Standard Tetris scoring system applies

### Online Multiplayer
- Best-of-5 rounds (first to 3 wins)
- Round ends when:
  - A player's stack reaches the top (elimination)
  - A player clears 30 lines (line goal victory)
- **Garbage Attack System:**
  - 2 lines cleared = 1 garbage line sent
  - 3 lines cleared = 2 garbage lines sent  
  - 4 lines cleared = 4 garbage lines sent
- Garbage lines appear at bottom of opponent's grid

## 🎯 Game Flow

1. **Round Start**: Both players begin with fresh grids
2. **Gameplay**: Players compete simultaneously
3. **Attack Phase**: Line clears send garbage to opponent
4. **Round End**: Determined by elimination or line goal
5. **Match Progress**: Track wins toward best-of-5
6. **Final Victory**: First to 3 round wins takes the match

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
├── launcher.py           # Main menu launcher 🆕
├── main.py              # Local battle (vs AI)
├── online_battle.py     # Online multiplayer 🆕
├── single_player.py     # Single player mode
├── config.py            # Constants & settings
├── game.py              # Core Tetris engine
├── tetromino.py         # Piece logic & generation
├── player.py            # Human input handling
├── network_player.py    # Network player class 🆕
├── ai_player.py         # AI decision making
├── sounds.py            # Audio system
├── network_protocol.py  # Network communication 🆕
├── network_test.py      # Connection testing 🆕
├── requirements.txt     # Dependencies
├── README.md           # Documentation
├── ONLINE_MULTIPLAYER.md # Online setup guide 🆕
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

### Optional Dependencies
- matplotlib 3.5.0+ (for AI battle statistics graphs)
  - Install with: `pip install matplotlib`
  - Game works perfectly without it, but you'll get beautiful post-round statistics

### Troubleshooting
- **AI Battle crashes?** Install matplotlib: `pip install matplotlib`
- **Network issues?** Run: `python network_test.py test`
- **Missing sounds?** Check `assets/sounds/` folder

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
