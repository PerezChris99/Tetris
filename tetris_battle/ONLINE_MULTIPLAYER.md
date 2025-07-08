# Tetris Battle - Online Multiplayer Guide

## 🌐 Online Multiplayer Overview

Tetris Battle now supports **real-time online multiplayer**, allowing you to battle against friends and players over the internet! The online mode features:

- **Real-time synchronization** between players
- **Garbage line attacks** when clearing multiple lines
- **Lag compensation** and network optimization
- **Automatic reconnection** handling
- **Cross-platform compatibility** (Windows, Mac, Linux)

## 🚀 Quick Start Guide

### Starting an Online Game

1. **Launch the Game**
   ```bash
   python launcher.py
   ```

2. **Choose Online Multiplayer**
   - Use arrow keys to select "Online Multiplayer"
   - Press ENTER to confirm

3. **Host or Join**
   - **Host Game**: You create a server that others connect to
   - **Join Game**: You connect to someone else's server

### Hosting a Game (Server)

1. Select **"Host Game"** from the online menu
2. Wait for the server to start (you'll see your IP and port)
3. **Share your connection info** with the other player:
   - IP Address: `192.168.1.100` (example)
   - Port: `12345` (example)
4. Wait for the other player to connect
5. The game starts automatically once connected!

### Joining a Game (Client)

1. Select **"Join Game"** from the online menu
2. Enter the **host's IP address** when prompted
3. Enter the **host's port number** when prompted
4. Wait for connection to establish
5. The game starts automatically once connected!

## 🔧 Network Setup

### Local Network (Same WiFi/LAN)

For players on the same local network (same house, office, etc.):

1. **Find your local IP address:**
   ```bash
   python network_test.py ip
   ```

2. **Use the local IP** (usually starts with `192.168.` or `10.`)
3. **No router configuration needed!**

### Internet Play (Different Networks)

For players on different internet connections:

#### Option 1: Port Forwarding (Recommended)
1. **Host configures port forwarding** on their router
2. **Forward the game port** (shown when hosting) to your computer
3. **Share your public IP** (find at whatismyip.com)

#### Option 2: VPN Services (Easier)
- Use services like **Hamachi**, **ZeroTier**, or **Radmin VPN**
- Both players join the same VPN network
- Use the VPN IP addresses to connect

#### Option 3: Cloud Gaming Services
- Use services like **ngrok** to create a tunnel
- Follow their setup guides for TCP tunneling

## 🛠️ Troubleshooting

### Network Connectivity Test

Run our built-in network test to diagnose issues:

```bash
python network_test.py test
```

This will check:
- ✅ Local IP address detection
- ✅ Server creation capability  
- ✅ Loopback connections
- ✅ Internet connectivity
- ✅ Available ports

### Common Issues & Solutions

#### "Cannot create server"
- **Check firewall settings** (allow Python/game through)
- **Run as administrator** (Windows)
- **Try a different port** (if prompted)

#### "Connection failed" 
- **Verify IP address and port** are correct
- **Check if host is running** and waiting for connections
- **Test connectivity:** `python network_test.py check <host> <port>`

#### "Connection drops during game"
- **Check internet stability** on both ends
- **Close bandwidth-heavy applications** (streaming, downloads)
- **Try a VPN connection** for more stable routing

#### "Game feels laggy"
- Network latency affects responsiveness
- **Use wired connections** when possible
- **Connect to geographically closer players**
- Current implementation optimizes for <200ms latency

## 🎮 Online Gameplay Features

### Synchronized Game State
- **Real-time piece movement** synchronization
- **Shared random piece sequences** (both players get same pieces)
- **Synchronized line clearing** animations
- **Live score and statistics** updates

### Attack System
- **Send garbage lines** when clearing 2+ lines simultaneously:
  - 2 lines = 1 garbage line
  - 3 lines = 2 garbage lines  
  - 4 lines (Tetris) = 4 garbage lines
- **Garbage lines appear at bottom** of opponent's grid
- **Strategic play** - time your attacks for maximum impact!

### Win Conditions
- **Elimination**: Opponent's grid fills up (game over)
- **Line Goal**: First to clear 30 lines wins the round
- **Best of 5**: First player to win 3 rounds wins the match

## 📋 Controls (Online Mode)

| Key | Action |
|-----|--------|
| ← → | Move piece left/right |
| ↑ | Rotate piece |
| ↓ | Soft drop (faster) |
| Space | Hard drop (instant) |
| M | Toggle sound on/off |
| R | Restart game (when ended) |
| Esc | Return to menu |

## 🔒 Network Security

### Safe Connection Practices
- **Only connect to trusted players** you know
- **Be cautious with public IP sharing** 
- **Use VPN services** for additional security
- **Don't share ports unnecessarily**

### Firewall Configuration
The game uses standard TCP connections and only requires:
- **One port open** for the host (automatically assigned)
- **Outbound connections allowed** for the joiner
- **No special protocols** or elevated privileges

## 🚀 Performance Tips

### For Best Online Experience
1. **Stable internet connection** (wired preferred)
2. **Close bandwidth-heavy apps** during play
3. **Choose nearby players** when possible
4. **Use game mode on routers** if available
5. **Update network drivers** regularly

### Network Requirements
- **Minimum:** 56k dial-up connection
- **Recommended:** Broadband (1+ Mbps)
- **Latency:** Best under 200ms, playable up to 500ms
- **Data usage:** ~1-5 KB/second during active play

## 🏆 Competitive Play

### Tournament Mode
While not built-in yet, you can organize tournaments using:
- **Round-robin format** with multiple players
- **Best-of-X series** (configure ROUNDS_TO_WIN in config.py)
- **Time limits** for each match
- **Score tracking** across multiple sessions

### Recording Games
- The game displays live statistics during play
- Screenshot tools can capture final scores
- Consider streaming software for recording matches

## 🔮 Future Enhancements

Planned features for future versions:
- **Lobby system** with multiple rooms
- **Spectator mode** for watching games
- **Replay system** for reviewing matches
- **Global leaderboards** and rankings
- **Tournament bracket system**
- **Custom game modes** and rules

## 📞 Support & Community

### Getting Help
1. **Read this guide thoroughly**
2. **Run network diagnostics:** `python network_test.py test`
3. **Check firewall and router settings**
4. **Try VPN solutions** for difficult connections

### Reporting Issues
When reporting network issues, please include:
- Your operating system
- Network test results
- Error messages (if any)
- Connection type (local/internet)
- Both players' setup details

### Community
- Share your best online matches!
- Organize tournaments with friends
- Create strategy guides for online play
- Help other players with setup issues

---

## 🎯 Ready to Battle Online!

You're now ready to enjoy **Tetris Battle** with players around the world! 

**Quick reminder of the process:**
1. Launch with `python launcher.py`
2. Choose "Online Multiplayer"  
3. Host or Join a game
4. Share/enter connection details
5. Battle in real-time!

Have fun and may the best Tetris player win! 🏆
