# Quick Start Guide - Robot Navigation AI Simulator

## Installation (One-Time Setup)

### Step 1: Install Python Dependencies
```bash
pip install pyside6 qt-material pyqtgraph
```

### Step 2: Verify Installation
```bash
python -c "import PySide6; print('PySide6 OK')"
python -c "import qt_material; print('qt-material OK')"
python -c "import pyqtgraph; print('pyqtgraph OK')"
```

## Running the Application

### Simple Launch
```bash
python robot_navigation_simulator.py
```

The application window will open automatically with a professional desktop interface.

## Using the Application

### 1. Welcome Screen
- Click **"Start Simulation"** to begin
- Click **"About Project"** for information
- Click **"Exit"** to close the application

### 2. Configuration Screen
**Left Panel - Difficulty:**
- **Easy**: 10% obstacles (easier navigation)
- **Medium**: 25% obstacles (balanced challenge)
- **Hard**: 40% obstacles (maximum difficulty)

**Right Panel - Speed:**
- **Slow**: 500ms per step (best for observation)
- **Normal**: 200ms per step (default)
- **Fast**: 50ms per step (quick visualization)

Click **"Start Simulation"** to begin with your selected options.

### 3. Simulation Dashboard
The main window has three sections:

**Left Panel (Movement History)**
- Shows step-by-step movements of the robot
- Updates in real-time as robot navigates
- Scrolls to show last 10 movements

**Center Panel (Grid Visualization)**
- 20x20 grid environment
- Blue circle: Robot current position
- Green square: Goal/target location
- Dark blocks: Obstacles
- Orange cells: Nodes explored by A* algorithm
- Green path: Final optimal route found

**Right Panel (Telemetry)**
- Position: Robot's current (x, y) coordinates
- Steps: Total moves taken by robot
- Explored: Number of nodes analyzed by A*
- Time: Elapsed time since simulation start
- Speed: Current simulation speed setting
- Status: Current state (Running/Complete)

**Control Buttons**
- **Pause**: Freeze simulation for observation
- **Resume**: Continue paused simulation
- **Terminate**: Stop simulation and return to config
- **Retry Same Grid**: Run same grid layout again
- **Generate New Grid**: Create new random grid
- **Back to Config**: Return to configuration screen

### 4. Analytics Summary Screen
After simulation completes:
- **Total Steps**: How many moves the robot made
- **Path Length**: Number of cells in optimal path
- **Nodes Explored**: How many cells A* algorithm evaluated
- **Elapsed Time**: Total runtime in seconds
- **Efficiency**: Ratio of path length to nodes explored (lower is better)

Click **"Return to Welcome"** to start a new simulation.

## Tips & Tricks

### For Best Learning Experience
1. Start with **Easy** difficulty and **Slow** speed
2. Watch the orange cells light up to see A* exploration pattern
3. Notice how the robot follows the green optimal path
4. Compare different difficulty levels to see algorithm adaptation

### For Quick Demonstrations
1. Use **Hard** difficulty for challenging scenarios
2. Select **Fast** speed for rapid visualization
3. Click "Generate New Grid" multiple times to see variety

### Understanding the Algorithm
- Orange cells = Nodes A* algorithm evaluated
- Appears to "fan out" from start, moving toward goal
- Green path = Result of A* finding optimal route
- Robot follows green path without backtracking

## Troubleshooting Quick Fixes

| Problem | Solution |
|---------|----------|
| "No module named 'PySide6'" | Run: `pip install pyside6` |
| Application won't start | Ensure Python 3.8+ installed: `python --version` |
| Grid not visible | Try selecting different difficulty level |
| Simulation very slow | Change to "Fast" speed in config |
| Button clicks not working | Wait for previous animation to complete |

## System Requirements
- Python 3.8 or higher
- Windows, macOS, or Linux
- ~100MB disk space for dependencies
- No special GPU required

## File Location
```
robot_navigation_simulator.py    ← Main application (run this file)
```

## Command-Line Execution Examples

```bash
# Run from command line
cd path/to/robot-navigation
python robot_navigation_simulator.py

# On Windows PowerShell
.\venv\Scripts\Activate.ps1  # if using virtual environment
python robot_navigation_simulator.py

# On macOS/Linux
source venv/bin/activate  # if using virtual environment
python robot_navigation_simulator.py
```

## What is A* Pathfinding?
A* is an intelligent pathfinding algorithm that:
1. Evaluates multiple possible paths simultaneously
2. Uses a heuristic (distance) to guide the search toward the goal
3. Finds the optimal route efficiently
4. Common in game AI and robotics

The orange cells show nodes the algorithm considered. Notice:
- It "searches outward" intelligently
- Focuses more toward the goal direction
- Avoids dead ends when possible
- Finds shortest path avoiding obstacles

## Getting Help

### Check Application State
- Read the Status in the Telemetry panel
- Watch the Movement History for robot actions
- Look at grid visualization for path and obstacles

### Verify Dependencies
```bash
pip list | findstr /I "pyside6 qt-material pyqtgraph"
```

### Reinstall if Issues Persist
```bash
pip uninstall pyside6 qt-material pyqtgraph -y
pip install pyside6 qt-material pyqtgraph
```

## For More Information
See: `ROBOT_NAVIGATION_SIMULATOR_README.md` for detailed documentation

---

**Quick Summary**: Install packages → Run file → Select settings → Watch A* algorithm navigate the grid → Review analytics
