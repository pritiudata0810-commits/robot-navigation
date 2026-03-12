# 🤖 Robot Navigation Simulator

A professional terminal-based robot navigation game featuring A* pathfinding, fog of war, and real-time visualization using the Rich library.

## Features

### ✨ Core Features
- **A* Pathfinding**: Optimal shortest-path algorithm with heuristic search
- **Explored Node Tracking**: Visualize every tile the algorithm checked (·)
- **Fog of War (Sensor Range)**: 3-tile radius reveals walls and paths as robot moves
- **Multiple Difficulty Levels**:
  - Easy: 10% walls
  - Medium: 25% walls
  - Hard: 40% walls
- **Configurable Animation Speed**:
  - Slow: 1.0s per step
  - Normal: 0.5s per step
  - Fast: 0.2s per step

### 🎮 Visual Elements
- 🤖 Robot (current position)
- 🧱 Walls (discovered obstacles)
- 🏁 Goal (destination)
- 🟦 Open paths
- · Explored nodes (A* search history)
- ⬜ Hidden/unexplored areas
- ⬛ Hidden walls

### 📊 Statistics Display
- Current coordinates (X, Y)
- Total steps taken
- Path length
- **Computational Stats**:
  - Nodes Explored: Total unique cells checked by A*
  - Efficiency: (Path Length / Nodes Explored) × 100%
  - Time: Milliseconds to compute path

## Requirements

- Python 3.7+
- Rich library

## Installation

1. Clone or download the repository
2. Install the Rich library:
   ```bash
   pip install rich
   ```

## Usage

Run the simulator:
```bash
python navigator.py
```

### Main Menu
1. **Select Difficulty**: Choose Easy, Medium, or Hard
2. **Select Speed**: Choose Slow, Normal, or Fast
3. Press Enter to start the animation

### Gameplay
- Watch the robot navigate from start (top-left) to goal (bottom-right)
- Gray dots (·) show where the A* algorithm explored
- Watch the fog of war reveal walls within the 3-tile sensor range
- Real-time stats update as the robot moves
- Goal reached when robot reaches the bottom-right corner

### Play Again
After reaching the goal, choose to play again or exit.

## How It Works

### Grid Generation
- 15×15 grid with randomly placed obstacles
- DFS validation ensures a valid path always exists
- No path is ever blocked

### A* Algorithm
- Uses Manhattan distance heuristic
- Explores minimum necessary nodes to find optimal path
- Tracks every explored node for visualization

### Fog of War
- Initially hides all walls (shown as dark ⬛)
- Reveals tiles within 3-tile radius of robot position (Chebyshev distance)
- Uses different colors for discovered vs hidden areas
- Discovered areas maintain their state for visual continuity

### Performance Metrics
- **Nodes Explored**: Count of unique cells the algorithm evaluated
- **Efficiency**: Lower is better; shows how direct the path is
  - 100% = extremely efficient (rare)
  - 50% = good efficiency (common)
  - <10% = inefficient (very complex environment)
- **Time**: Milliseconds to calculate the path (typically <1ms)

## Code Structure

The script is organized into clear sections:

```
1. Enums & Data Classes
   - Difficulty levels
   - Animation speeds
   - Game configuration
   - A* metrics tracking

2. Grid Management (Grid class)
   - Grid initialization
   - Obstacle placement
   - Path validation using BFS

3. Game State (GameState class)
   - Robot position tracking
   - Movement management
   - Discovered tiles tracking

4. A* Pathfinding (AStar class)
   - Core A* algorithm
   - Heuristic function
   - Explored node tracking

5. Fog of War (FogOfWar class)
   - Sensor range management
   - Tile discovery tracking

6. UI & Visualization (Navigator class)
   - Main menu rendering
   - Grid rendering with emojis
   - Sidebar with stats
   - Live animation loop
```

## Tips

- **Study the Explored Nodes**: The gray dots (·) show how many extra tiles the algorithm had to check beyond the final path. More explored nodes = more complex environment.
- **Compare Efficiency**: The efficiency percentage reveals how "direct" your path is. Try different difficulties to see the impact.
- **Fog of War Strategy**: Notice how only a 3-tile radius around the robot is visible. This simulates realistic sensor limitations.

## Customization

You can easily customize the simulator by editing `navigator.py`:

```python
# Change grid size (default: 15)
grid_size: int = 15

# Change sensor range (default: 3)
sensor_range: int = 3

# Modify difficulty percentages
EASY = 0.10      # 10% walls
MEDIUM = 0.25    # 25% walls
HARD = 0.40      # 40% walls

# Adjust animation speeds
SLOW = 1.0       # 1 second per step
NORMAL = 0.5     # 0.5 seconds per step
FAST = 0.2       # 0.2 seconds per step
```

## Algorithm Complexity

- **Grid Generation**: O(n²) where n = grid size
- **A* Pathfinding**: O(n² log n) in worst case
- **Path Length**: Typically 24-30 steps for 15×15 grid
- **Computation Time**: Usually <1ms on modern hardware

## Author Notes

This simulator demonstrates:
- Advanced pathfinding algorithms (A*)
- Professional TUI design with Rich
- Real-time data visualization
- Game state management
- User interaction patterns

The fog of war and explored node visualization help understand how pathfinding algorithms work under the hood.

---

**Version**: 1.0  
**License**: MIT  
**Python**: 3.7+
