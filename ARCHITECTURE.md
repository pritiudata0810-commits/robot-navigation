# Robot Navigation Simulator - Architecture & Design

## Overview

The Robot Navigation Simulator is built with a clean, modular architecture that separates concerns into distinct components. The entire application fits in a single 644-line Python file with clear section boundaries.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Navigation (Main Controller)            │
│  - show_main_menu()      Show UI and get user selection    │
│  - initialize_game()     Setup grid, A*, fog of war        │
│  - run_animation()       Main game loop with live display  │
│  - render_*()            Various rendering methods         │
└─────────────────────────────────────────────────────────────┘
         ↓                    ↓                     ↓
    ┌─────────┐         ┌──────────┐         ┌──────────────┐
    │  Grid   │         │ GameState│         │ FogOfWar     │
    │---------|         │----------|         │______________|
    │ • Place │         │ • Position         │ • Sensor     │
    │   walls │         │ • Steps            │   range      │
    │ • Validate        │ • Path             │ • Discovery  │
    │   path  │         │ • Metrics          │   tracking   │
    └─────────┘         └──────────┘         └──────────────┘
         ↑                    ↑
         └────────────────────┘
              ↓
         ┌─────────────┐
         │   AStar     │
         │─────────────┤
         │ • Pathfind  │
         │ • Track     │
         │   explored  │
         │ • Compute   │
         │   metrics   │
         └─────────────┘
```

## Component Details

### 1. Data Classes & Enums (Lines 27-60)

**Difficulty Enum**
- EASY = 0.10 (10% walls)
- MEDIUM = 0.25 (25% walls)
- HARD = 0.40 (40% walls)

**Speed Enum**
- SLOW = 1.0s per step
- NORMAL = 0.5s per step
- FAST = 0.2s per step

**GameConfig**
- Stores: difficulty, speed, grid_size, sensor_range
- Passed to all components for consistent configuration

**AStarMetrics**
- nodes_explored: Count of examined tiles
- path_length: Number of steps in solution
- computation_time_ms: Milliseconds to pathfind
- explored_nodes: Set of all examined coordinates
- efficiency: Calculated property (path/nodes)

### 2. Grid Class (Lines 83-158)

**Purpose**: Manages the 15×15 game board

**Key Methods**:
- `__init__()` - Initialize empty grid
- `is_walkable()` - Check if tile is valid path
- `get_neighbors()` - Return 4-connected neighbors
- `place_obstacles()` - Add random walls with validation
- `_has_valid_path()` - BFS to verify path exists

**Algorithm**: 
```
for N random positions:
    if not start/goal:
        place wall
        if path still exists:
            keep wall
        else:
            remove wall (no-op)
```

### 3. GameState Class (Lines 165-209)

**Purpose**: Tracks robot position and game statistics

**State Variables**:
- robot_pos: Current (x, y) coordinates
- steps: Movement counter
- path: A* solution path
- current_path_index: Position in path
- metrics: AStarMetrics from pathfinding
- is_finished: Goal reached flag
- discovered_tiles: Fog of war visibility set

**Key Methods**:
- `move_to_next()` - Advance robot along path
- `set_path()` - Store A* solution
- `_update_discovered_tiles()` - Fog of war reveal

### 4. AStar Class (Lines 212-289)

**Purpose**: Implement A* pathfinding algorithm

**Algorithm Overview**:
```
1. Initialize open_set with start position
2. While open_set not empty:
   a. Pop node with lowest f_score
   b. If at goal, reconstruct and return path
   c. For each neighbor:
      - Calculate tentative g_score
      - If better than previous, update
      - Add to open_set with f_score
3. Return path (or empty if no solution)
```

**Heuristic**: Manhattan distance
```
h(n) = |n.x - goal.x| + |n.y - goal.y|
```

**Metrics Tracking**:
- explored_nodes set captures all visited nodes
- computation_time_ms measures wall-clock time
- path_length from final solution

### 5. FogOfWar Class (Lines 292-323)

**Purpose**: Implement 3-tile sensor range revealing

**Sensor Shape**: Square (Chebyshev distance)
```
  7 8 9
  4 5 6
  1 2 3

Robot at 5, sensor range 1 = shows 1-9
Robot at 5, sensor range 3 = shows large square
```

**Key Methods**:
- `reveal_around()` - Add tiles within range to discovered
- `is_discovered()` - Check if tile visible

### 6. Navigator Class (Lines 326-629)

**Purpose**: Main game controller and UI renderer

**Main Methods**:

**show_main_menu()** (Lines 348-405)
- Display welcome panel
- Prompt for difficulty with Rich.prompt
- Prompt for speed with Rich.prompt
- Return GameConfig object

**initialize_game()** (Lines 407-434)
- Create Grid with obstacle percentage
- Call grid.place_obstacles()
- Run A* pathfinding
- Initialize FogOfWar
- Initial reveal around start

**render_grid()** (Lines 445-485)
- 15 lines of output, each with 15 cells
- Conditional rendering:
  - Robot position → 🤖
  - Goal position → 🏁
  - Walls (discovered) → 🧱
  - Walls (hidden) → ⬛
  - Explored nodes (discovered) → ·
  - Explored nodes (hidden) → ⬜
  - Paths (discovered) → 🟦
  - Paths (hidden) → ⬜

**render_sidebar()** (Lines 487-527)
- Position section: X, Y coordinates
- Movement section: steps, path length
- Stats section: explored, efficiency, time
- Status section: progress or goal reached

**render_display()** (Lines 529-551)
- Create Layout with 2 columns
- Grid on left (wider)
- Sidebar on right (30 char width)
- Both wrapped in Panels with styling

**run_animation()** (Lines 553-586)
- Use Rich.live for 10 fps updates
- Loop until goal reached:
  - Update display
  - Move robot
  - Reveal fog of war
  - Sleep based on speed
- Show completion panel with final stats

**run()** (Lines 588-629)
- Main entry point
- Catch KeyboardInterrupt
- Implement play-again loop
- Exception handling

## Data Flow

```
User Input (Menu)
       ↓
GameConfig
       ↓
Grid Generation → Obstacle Placement → Path Validation
       ↓
Initialize GameState
       ↓
A* Pathfinding → Explored Nodes Tracking → Metrics
       ↓
GameState.set_path() + GameState.metrics
       ↓
Animation Loop:
  ├─ Render Grid (with discovered tiles from fog)
  ├─ Render Sidebar (with metrics)
  ├─ Robot moves
  ├─ Fog of war reveals
  └─ [repeat until goal]
       ↓
Final Stats Display
       ↓
Play Again?
```

## Key Algorithms

### Manhattan Distance Heuristic
```python
def heuristic(pos, goal):
    return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])
```

### Chebyshev Distance (Fog of War)
```python
for dx, dy in directions:
    if max(abs(dx), abs(dy)) <= sensor_range:
        reveal(x + dx, y + dy)
```

### BFS Path Validation
```python
queue = [start]
visited = {start}
while queue:
    current = pop(queue)
    if current == goal: return True
    for neighbor in neighbors(current):
        if neighbor not in visited:
            add(queue, neighbor)
            add(visited, neighbor)
return False
```

## Performance Characteristics

| Operation | Complexity | Typical Time |
|-----------|-----------|--------------|
| Grid generation | O(n²) | 50-200ms |
| A* pathfinding | O(n² log n) | 0.1-1ms |
| Rendering grid | O(n²) | <1ms |
| Single animation frame | O(1) | <5ms |

## Resource Usage

- **Memory**: ~100KB for 15×15 grid + data structures
- **CPU**: Minimal during animation (10 fps capped)
- **File Size**: 644 lines, ~23KB source code

## Extensibility Points

To modify the simulator, edit these areas:

1. **Grid Size**: Line 50 `grid_size: int = 15`
2. **Sensor Range**: Line 51 `sensor_range: int = 3`
3. **Difficulty Levels**: Lines 32-35
4. **Animation Speeds**: Lines 39-42
5. **Emoji Icons**: Lines 461, 464, 467, 470, 473
6. **Colors/Styling**: Various Panel/Layout definitions

## Design Patterns Used

1. **Separation of Concerns**: Each class has single responsibility
2. **Data Classes**: Use @dataclass for clean initialization
3. **Enums**: Type-safe configuration values
4. **Rich Integration**: Clean UI abstraction
5. **Factory Pattern**: Navigator creates all components
6. **Strategy Pattern**: Different render methods for different displays

## Testing Considerations

To verify correctness:
1. Path exists before game (grid._has_valid_path)
2. A* finds optimal path (compare with BFS path length)
3. Metrics are consistent:
   - path_length = len(solution)
   - nodes_explored = len(explored_set)
   - efficiency = path_length / nodes_explored
4. Fog of war reveals correct tiles (Chebyshev distance)
5. Robot follows path exactly

---

**Architecture Version**: 1.0  
**Created**: 2026-03-12  
**Status**: Complete ✅
