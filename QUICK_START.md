# 🌃 CYBERPUNK MISSION CONTROL - QUICK START GUIDE

## 🚀 Launch the Dashboard

```bash
python navigator.py
```

## 🎮 Gameplay

### 1. Select Difficulty
- **Easy** (10% walls) - For beginners
- **Medium** (25% walls) - Balanced challenge  
- **Hard** (40% walls) - For veterans

### 2. Select Animation Speed
- **Slow** (1.0s per step) - Watch carefully
- **Normal** (0.5s per step) - Balanced pacing
- **Fast** (0.2s per step) - Quick playthrough

### 3. Start Mission
- Press Enter to launch the mission
- Watch the robot navigate to the goal (🏁)
- Avoid hazards marked with ✕

### 4. Victory
- When the robot reaches the goal, you'll see a full-screen **"SYSTEM CLEAR"** banner
- View the mission summary with all stats
- Choose to play again or exit

## 🎨 Understanding the Dashboard

### Left Panel: HEX STREAM
- Scrolling hexadecimal "sensor data" feed
- Simulates real-time data transmission
- Colors fade: Bright Cyan → Dim Blue
- Updates every 3 frames

### Center Panel: SECTOR MAP
The main 15×15 navigation grid showing:
- 🤖 Your robot (Bright Cyan)
- 🏁 Goal location (Magenta)
- ✕ Dynamic hazards (Red, moving)
- · Explored tiles (with depth coloring)
- █ Walls (Dark Blue)
- ⚡ Particle trails (fading movement)

**Visual Effects:**
- Radar pulse: Expanding circle from robot
- Heatmap: Visited tiles glow and fade
- Scanlines: CRT monitor effect (every 3 rows)
- A* frontier: Flickering yellow exploration dots

### Right Panel: TELEMETRY
Real-time mission statistics:
- **POS**: Current robot coordinates
- **STEPS**: Progress (current/total)
- **TIME**: A* computation time
- **PROGRESS**: Visual bar chart
- **NODES**: Explored nodes count
- **EFFICIENCY**: Path quality percentage

### Top Bar: SATELLITE LINK
Mission control status display:
- **Link Status**: STABLE/SIGNAL (flickers)
- **CPU Load**: Simulated system load (30-60%)
- **Coordinate Mapping**: Scanning progress bar
- **Red Alert**: Appears when hazards are close

## 📊 Visual Effects Explained

| Effect | What It Means | Colors |
|--------|---------------|--------|
| Radar Pulse | Scanning nearby area | Cyan expanding ring |
| Heatmap Glow | Recently visited | Cyan→Blue→Purple fade |
| Particle Trail | Robot movement | ⚡¤· cycling |
| Yellow Flicker | A* pathfinding | Flickering yellow dots |
| Red Alert | Danger nearby | Red bold text |
| Scanlines | Retro CRT effect | Dark scanline bars |

## 🎯 Tips & Tricks

### Optimizing Your Route
- **Higher Efficiency** = Fewer nodes explored vs path length
- **Lower Node Count** = Better A* heuristic (open areas)
- **Hard Difficulty** = More obstacles = potentially higher efficiency

### Watching the Algorithm
- Watch yellow flickering nodes to see A* "thinking"
- Particles show the exact path robot takes
- Heatmap shows exploration progress

### Performance
- **Fast Speed** + **Easy Difficulty** = Quickest win
- **Slow Speed** + **Hard Difficulty** = Best for studying behavior
- Animation maintains smooth 50ms frames even on slow machines

## 📈 Performance Metrics Explained

Shown in the final "SYSTEM CLEAR" banner:

- **Total Steps**: Number of moves (≥ Path Length)
- **Path Length**: Optimal route length from A*
- **Nodes Explored**: How many tiles A* evaluated
- **Efficiency**: (Path Length / Nodes Explored) × 100%
  - Higher = more efficient exploration
  - Lower = more exploration needed
- **Computation Time**: Time to calculate path in milliseconds

## 🛠️ Test Scripts

Verify the installation:
```bash
python test_cyberpunk.py       # Component tests
python test_integration.py     # Full pipeline test
python validate_features.py    # Feature checklist
```

## 🎭 Visual Customization (Advanced)

The cyberpunk theme is defined in `CyberpunkTheme` class:
- Edit colors in the static color definitions
- Modify particle characters: `⚡¤·` → your choice
- Adjust animation speeds in `AnimationState`
- Change hazard count in `_spawn_hazards()`

## 📱 Keyboard Controls

- **Main Menu**: Type difficulty/speed choices + Enter
- **Game Start**: Press Enter to begin animation
- **During Game**: Watch automatically (no input needed)
- **Final Screen**: Answer "Play again?" with Y/N

## 🚨 Troubleshooting

### Grid appears empty
- May be a terminal width issue
- Try maximizing your terminal window
- Some effects require 100+ character width

### Colors not showing
- Ensure terminal supports ANSI colors
- On Windows, use Windows Terminal (not cmd.exe)
- Rich library automatically detects color support

### Animation too slow/fast
- Adjust Speed setting at startup
- Frame timing is 50ms per update
- CPU load indicator helps diagnose performance

## 📚 More Information

See **CYBERPUNK_FEATURES.md** for:
- Detailed feature descriptions
- Technical implementation details
- Code structure explanation
- Customization ideas

---

**MISSION CONTROL READY** 🚀
Stay sharp, agent. Time to navigate.
