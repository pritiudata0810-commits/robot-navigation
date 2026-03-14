# Robot Navigation AI Simulator

A professional graphical AI simulation that demonstrates grid-based robot navigation using the A* pathfinding algorithm.

## Overview

This is **NOT a user-controlled game**. The robot is controlled completely by an AI "brain" that:
- Analyzes the grid and obstacles
- Computes the shortest path using A* algorithm
- Visualizes the exploration process
- Animates the robot moving along the optimal path

The user simply:
- Selects difficulty level and simulation speed
- Starts the simulation
- Observes how the AI solves the navigation problem

## Installation

```bash
pip install customtkinter
```

## Running the Simulator

```bash
python navigator_ai_simulation.py
```

## UI Layout

### Left Panel - Control Panel
- **Difficulty Selection**: Easy (10% obstacles), Medium (25%), Hard (40%)
- **Speed Control**: Slow, Normal, or Fast animation speed
- **Buttons**:
  - Start Simulation: Begin pathfinding and animation
  - Generate New Grid: Create a new random grid
  - Reset Simulation: Reset without regenerating the grid

### Center Panel - Grid Visualization
- **20×20 grid** showing the navigation environment
- **Color coding**:
  - Bright Cyan: Robot
  - Bright Green: Goal
  - Dark Grey: Obstacles
  - Light Cyan: Explored nodes (during pathfinding)
  - Yellow: Final computed path
  - Dark shades: Empty cells

### Right Panel - Telemetry
Real-time simulation data:
- Robot Position (X, Y coordinates)
- Steps Taken (movements along path)
- Nodes Explored (A* algorithm search space)
- Elapsed Time (simulation duration)
- Speed Setting
- Status (Ready, Finding path, Animating robot, Goal reached)

## How It Works

### 1. Grid Generation
- Randomly places obstacles based on difficulty
- Sets robot start position (top-left, 0,0)
- Sets goal position (bottom-right, 19,19)
- Validates that goal is always reachable

### 2. A* Pathfinding
- Uses Manhattan distance as heuristic
- Gradually explores nodes (shown in cyan)
- Computes optimal shortest path
- Highlights path in yellow

### 3. Robot Animation
- Moves one cell at a time
- Speed controlled by user setting
- Real-time telemetry updates

### 4. Completion
- Shows victory message with statistics
- Displays: Total steps, elapsed time, path length, nodes explored
- Allows replay with same or new grid

## Code Structure

```
navigator_ai_simulation.py
├── Configuration & Constants
│   ├── Difficulty enum
│   ├── Speed enum
│   └── Color scheme
├── Node (dataclass for A*)
├── Grid class
│   ├── Grid generation
│   ├── Obstacle placement
│   ├── Walkability checks
│   └── Neighbor lookup
├── AStarPathfinder class
│   └── A* algorithm implementation
├── Robot class
│   ├── Position tracking
│   ├── Path following
│   └── Movement execution
├── SimulationUI class
│   ├── UI setup
│   ├── Drawing & animation
│   ├── Telemetry updates
│   └── Simulation control
└── main() entry point
```

## Key Features

✓ **Professional Dark Mode** - Modern robotics visualization theme  
✓ **Real-time Pathfinding Visualization** - See exploration in action  
✓ **A* Algorithm** - Optimal pathfinding with Manhattan distance heuristic  
✓ **Smooth Animation** - Configurable robot movement speed  
✓ **Dynamic Grid Generation** - Random obstacles with difficulty control  
✓ **Live Telemetry** - Real-time statistics and status updates  
✓ **Replay Capability** - Run multiple simulations  
✓ **Modularity** - Clean class-based design for easy extension  

## Technical Details

- **Language**: Python 3
- **GUI Framework**: customtkinter (modern tkinter theme)
- **Algorithm**: A* with 4-directional movement
- **Grid Size**: 20×20 cells
- **Cell Size**: 25×25 pixels
- **Heuristic**: Manhattan distance (|x1-x2| + |y1-y2|)

## Difficulty Levels

| Difficulty | Obstacle Density | Challenge |
|-----------|------------------|-----------|
| Easy      | 10%              | Minimal obstacles, longer paths |
| Medium    | 25%              | Balanced difficulty |
| Hard      | 40%              | Dense obstacles, complex pathfinding |

## Speed Settings

| Speed  | Delay (ms) | Animation |
|--------|-----------|-----------|
| Slow   | 500ms     | Leisurely movement |
| Normal | 200ms     | Standard pace |
| Fast   | 50ms      | Quick animation |

## Example Workflow

1. Launch the simulator: `python navigator_ai_simulation.py`
2. Select "Hard" difficulty
3. Select "Normal" speed
4. Click "Start Simulation"
5. Watch as the AI:
   - Explores the grid with cyan highlights
   - Discovers the optimal path (yellow highlight)
   - Animates the robot moving along the path (bright cyan dot)
6. View completion statistics
7. Click "Run Again" to replay or "Generate New Grid" for a new challenge

## Design Notes

This simulator demonstrates:
- **AI Decision Making**: A* algorithm selects optimal path
- **Heuristic Search**: Using Manhattan distance to guide exploration
- **Real-time Visualization**: Understanding algorithm behavior
- **Modular Design**: Clean separation between grid, pathfinding, UI, and animation
- **State Management**: Proper tracking of robot position, path, and telemetry

---

**Created with clean, professional Python code. No modifications to existing navigator.py or navigator_fixed.py files.**
