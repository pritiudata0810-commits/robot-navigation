"""
Robot Navigation Simulator with A* Pathfinding & Fog of War
A professional TUI-based game using Rich library featuring:
- A* pathfinding with explored node tracking
- Difficulty selection and animation speed control
- Fog of war (sensor range) with discovered tiles tracking
- Real-time visualization with Rich library
- Performance metrics (nodes explored, efficiency, computation time)
"""

import random
import time
from typing import List, Tuple, Set, Dict, Optional
from dataclasses import dataclass, field
from enum import Enum
from collections import deque
import heapq
from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.prompt import Prompt, Confirm
import math


# ============================================================================
# ENUMS & DATA CLASSES
# ============================================================================

class Difficulty(Enum):
    """Difficulty levels with corresponding wall percentages"""
    EASY = 0.10
    MEDIUM = 0.25
    HARD = 0.40


class Speed(Enum):
    """Animation speeds with corresponding sleep durations"""
    SLOW = 1.0
    NORMAL = 0.5
    FAST = 0.2


@dataclass
class GameConfig:
    """Configuration for the game session"""
    difficulty: Difficulty
    speed: Speed
    grid_size: int = 15
    sensor_range: int = 3


@dataclass
class AStarMetrics:
    """Metrics collected during A* execution"""
    nodes_explored: int = 0
    path_length: int = 0
    computation_time_ms: float = 0.0
    explored_nodes: Set[Tuple[int, int]] = field(default_factory=set)

    @property
    def efficiency(self) -> float:
        """Calculate efficiency: (path_length / nodes_explored) * 100"""
        if self.nodes_explored == 0:
            return 0.0
        return (self.path_length / self.nodes_explored) * 100


# ============================================================================
# GRID MANAGEMENT
# ============================================================================

class Grid:
    """
    Manages the 15x15 game grid with obstacles and validation.
    """
    
    def __init__(self, size: int = 15, obstacle_percentage: float = 0.1):
        """
        Initialize grid.
        
        Args:
            size: Grid dimensions (size x size)
            obstacle_percentage: Percentage of tiles that should be walls (0.0-0.99)
        """
        self.size = size
        self.obstacle_percentage = obstacle_percentage
        self.grid = [[False for _ in range(size)] for _ in range(size)]
        self.start_pos: Tuple[int, int] = (0, 0)
        self.goal_pos: Tuple[int, int] = (size - 1, size - 1)
    
    def is_walkable(self, x: int, y: int) -> bool:
        """Check if a tile is within bounds and not a wall"""
        if 0 <= x < self.size and 0 <= y < self.size:
            return not self.grid[y][x]
        return False
    
    def get_neighbors(self, x: int, y: int) -> List[Tuple[int, int]]:
        """Get all valid neighboring tiles (4-directional: up, down, left, right)"""
        neighbors = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if self.is_walkable(nx, ny):
                neighbors.append((nx, ny))
        return neighbors
    
    def place_obstacles(self) -> None:
        """
        Generate random obstacles ensuring a valid path exists from start to goal.
        Uses DFS to validate that a path is always available.
        """
        # Calculate total obstacles needed
        total_tiles = self.size * self.size - 2  # Exclude start and goal
        num_obstacles = int(total_tiles * self.obstacle_percentage)
        
        # Place obstacles randomly
        obstacles_placed = 0
        attempts = 0
        max_attempts = total_tiles * 2
        
        while obstacles_placed < num_obstacles and attempts < max_attempts:
            x = random.randint(0, self.size - 1)
            y = random.randint(0, self.size - 1)
            
            # Don't place obstacles on start or goal
            if (x, y) not in [self.start_pos, self.goal_pos]:
                if not self.grid[y][x]:  # Not already an obstacle
                    self.grid[y][x] = True
                    
                    # Validate path still exists
                    if self._has_valid_path():
                        obstacles_placed += 1
                    else:
                        # Remove obstacle if it blocks all paths
                        self.grid[y][x] = False
            
            attempts += 1
        
        # Final validation
        if not self._has_valid_path():
            raise RuntimeError("Failed to generate grid with valid path")
    
    def _has_valid_path(self) -> bool:
        """
        Check if a valid path exists from start to goal using BFS.
        Used to validate obstacles don't block all paths.
        """
        visited = set()
        queue = deque([self.start_pos])
        visited.add(self.start_pos)
        
        while queue:
            x, y = queue.popleft()
            
            if (x, y) == self.goal_pos:
                return True
            
            for nx, ny in self.get_neighbors(x, y):
                if (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append((nx, ny))
        
        return False


# ============================================================================
# GAME STATE
# ============================================================================

class GameState:
    """Tracks robot position, movement, and game statistics."""
    
    def __init__(self, grid: Grid, config: GameConfig):
        self.grid = grid
        self.config = config
        self.robot_pos = grid.start_pos
        self.steps = 0
        self.path: List[Tuple[int, int]] = []
        self.current_path_index = 0
        self.metrics = AStarMetrics()
        self.is_finished = False
        self.discovered_tiles: Set[Tuple[int, int]] = set()
    
    def move_to_next(self) -> None:
        """Move robot to the next position along the path"""
        if self.current_path_index < len(self.path):
            self.robot_pos = self.path[self.current_path_index]
            self.steps += 1
            self.current_path_index += 1
            
            # Update fog of war
            self._update_discovered_tiles()
            
            if self.current_path_index >= len(self.path):
                self.is_finished = True
    
    def set_path(self, path: List[Tuple[int, int]]) -> None:
        """Set the path the robot will follow"""
        self.path = path
        self.current_path_index = 0
        self.metrics.path_length = len(path)
    
    def _update_discovered_tiles(self) -> None:
        """Reveal tiles within sensor range of current position"""
        x, y = self.robot_pos
        sensor_range = self.config.sensor_range
        
        for dx in range(-sensor_range, sensor_range + 1):
            for dy in range(-sensor_range, sensor_range + 1):
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.grid.size and 0 <= ny < self.grid.size:
                    # Use Chebyshev distance (max of abs differences) for square radius
                    if max(abs(dx), abs(dy)) <= sensor_range:
                        self.discovered_tiles.add((nx, ny))


# ============================================================================
# A* PATHFINDING ALGORITHM
# ============================================================================

class AStar:
    """
    A* pathfinding algorithm with metrics tracking.
    """
    
    def __init__(self, grid: Grid):
        self.grid = grid
    
    def find_path(self) -> Tuple[List[Tuple[int, int]], AStarMetrics]:
        """
        Find shortest path from grid start to goal using A* algorithm.
        
        Returns:
            Tuple of (path, metrics)
        """
        start = self.grid.start_pos
        goal = self.grid.goal_pos
        
        start_time = time.time()
        
        # Initialize open and closed sets
        open_set = []
        heapq.heappush(open_set, (0, start))
        
        # Track came_from, g_score, and explored nodes
        came_from: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {start: None}
        g_score = {start: 0}
        explored_nodes: Set[Tuple[int, int]] = set()
        
        while open_set:
            _, current = heapq.heappop(open_set)
            explored_nodes.add(current)
            
            if current == goal:
                # Reconstruct path
                path = self._reconstruct_path(came_from, current)
                
                # Calculate metrics
                computation_time = (time.time() - start_time) * 1000  # Convert to ms
                metrics = AStarMetrics(
                    nodes_explored=len(explored_nodes),
                    path_length=len(path),
                    computation_time_ms=computation_time,
                    explored_nodes=explored_nodes
                )
                return path, metrics
            
            # Check neighbors
            for neighbor in self.grid.get_neighbors(current[0], current[1]):
                tentative_g = g_score[current] + 1
                
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + self._heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score, neighbor))
        
        # No path found
        computation_time = (time.time() - start_time) * 1000
        metrics = AStarMetrics(
            nodes_explored=len(explored_nodes),
            computation_time_ms=computation_time,
            explored_nodes=explored_nodes
        )
        return [], metrics
    
    @staticmethod
    def _heuristic(pos: Tuple[int, int], goal: Tuple[int, int]) -> float:
        """Manhattan distance heuristic"""
        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])
    
    @staticmethod
    def _reconstruct_path(came_from: Dict[Tuple[int, int], Optional[Tuple[int, int]]], 
                         current: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Reconstruct path from came_from mapping"""
        path = [current]
        while came_from[current] is not None:
            current = came_from[current]
            path.append(current)
        return list(reversed(path))


# ============================================================================
# FOG OF WAR
# ============================================================================

class FogOfWar:
    """Manages the fog of war (sensor range) and tile discovery."""
    
    def __init__(self, grid: Grid, sensor_range: int = 3):
        self.grid = grid
        self.sensor_range = sensor_range
        self.discovered_tiles: Set[Tuple[int, int]] = set()
    
    def reveal_around(self, x: int, y: int) -> None:
        """Reveal all tiles within sensor range of position (x, y)"""
        for dx in range(-self.sensor_range, self.sensor_range + 1):
            for dy in range(-self.sensor_range, self.sensor_range + 1):
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.grid.size and 0 <= ny < self.grid.size:
                    # Use Chebyshev distance for square sensor area
                    if max(abs(dx), abs(dy)) <= self.sensor_range:
                        self.discovered_tiles.add((nx, ny))
    
    def is_discovered(self, x: int, y: int) -> bool:
        """Check if a tile has been discovered"""
        return (x, y) in self.discovered_tiles


# ============================================================================
# UI & VISUALIZATION
# ============================================================================

class Navigator:
    """Main game controller and UI renderer"""
    
    def __init__(self):
        self.console = Console()
        self.config: Optional[GameConfig] = None
        self.grid: Optional[Grid] = None
        self.game_state: Optional[GameState] = None
        self.astar: Optional[AStar] = None
        self.fog_of_war: Optional[FogOfWar] = None
    
    def show_main_menu(self) -> GameConfig:
        """Display main menu and get user selections"""
        self.console.clear()
        
        # Welcome panel
        welcome = Panel(
            "[bold cyan]🤖 ROBOT NAVIGATION SIMULATOR 🤖[/bold cyan]\n"
            "[yellow]A* Pathfinding with Fog of War[/yellow]",
            border_style="bright_blue",
            padding=(1, 2),
            expand=False
        )
        self.console.print(welcome)
        self.console.print()
        
        # Difficulty selection
        difficulty_panel = Panel(
            "[bold green]DIFFICULTY LEVELS[/bold green]\n"
            "[cyan]Easy[/cyan]     → 10% walls (easier navigation)\n"
            "[yellow]Medium[/yellow]  → 25% walls (balanced)\n"
            "[red]Hard[/red]     → 40% walls (challenging)",
            border_style="green",
            padding=(1, 2)
        )
        self.console.print(difficulty_panel)
        
        difficulty_input = Prompt.ask(
            "[bold]Select Difficulty[/bold]",
            choices=["easy", "medium", "hard"],
            default="medium"
        ).lower()
        
        difficulty_map = {
            "easy": Difficulty.EASY,
            "medium": Difficulty.MEDIUM,
            "hard": Difficulty.HARD
        }
        selected_difficulty = difficulty_map[difficulty_input]
        self.console.print(f"[green]✓ Difficulty: {selected_difficulty.name}[/green]")
        self.console.print()
        
        # Speed selection
        speed_panel = Panel(
            "[bold green]ANIMATION SPEED[/bold green]\n"
            "[cyan]Slow[/cyan]    → 1.0s per step (watch carefully)\n"
            "[yellow]Normal[/yellow]  → 0.5s per step (balanced)\n"
            "[magenta]Fast[/magenta]   → 0.2s per step (quick view)",
            border_style="green",
            padding=(1, 2)
        )
        self.console.print(speed_panel)
        
        speed_input = Prompt.ask(
            "[bold]Select Speed[/bold]",
            choices=["slow", "normal", "fast"],
            default="normal"
        ).lower()
        
        speed_map = {
            "slow": Speed.SLOW,
            "normal": Speed.NORMAL,
            "fast": Speed.FAST
        }
        selected_speed = speed_map[speed_input]
        self.console.print(f"[green]✓ Speed: {selected_speed.name}[/green]")
        self.console.print()
        
        self.console.print("[bold blue]⏳ Initializing game...[/bold blue]")
        
        return GameConfig(difficulty=selected_difficulty, speed=selected_speed)
    
    def initialize_game(self, config: GameConfig) -> None:
        """Initialize grid, pathfinding, and game state"""
        self.config = config
        
        # Create and populate grid
        self.grid = Grid(size=config.grid_size, obstacle_percentage=config.difficulty.value)
        self.grid.place_obstacles()
        
        # Initialize game state
        self.game_state = GameState(self.grid, config)
        
        # Initialize pathfinding
        self.astar = AStar(self.grid)
        path, metrics = self.astar.find_path()
        
        self.game_state.set_path(path)
        self.game_state.metrics = metrics
        
        # Initialize fog of war
        self.fog_of_war = FogOfWar(self.grid, sensor_range=config.sensor_range)
        
        # Initial reveal (around start position)
        self.fog_of_war.reveal_around(*self.grid.start_pos)
        self.game_state.discovered_tiles = self.fog_of_war.discovered_tiles.copy()
    
    def render_grid(self) -> str:
        """
        Render the game grid with all visual elements.
        
        Returns:
            String representation of the grid
        """
        if not self.grid or not self.game_state:
            return ""
        
        grid_lines = []
        
        for y in range(self.grid.size):
            line = ""
            for x in range(self.grid.size):
                pos = (x, y)
                
                # Robot position
                if pos == self.game_state.robot_pos:
                    line += "🤖"
                # Goal position
                elif pos == self.grid.goal_pos:
                    line += "🏁"
                # Wall (only show if discovered)
                elif self.grid.grid[y][x]:
                    if pos in self.game_state.discovered_tiles:
                        line += "🧱"
                    else:
                        line += "⬛"  # Hidden wall (dark)
                # Explored nodes (light grey dot)
                elif pos in self.game_state.metrics.explored_nodes:
                    if pos in self.game_state.discovered_tiles:
                        line += "·"
                    else:
                        line += "⬜"  # Hidden explored node
                # Regular path
                else:
                    if pos in self.game_state.discovered_tiles:
                        line += "🟦"
                    else:
                        line += "⬜"  # Hidden path
            
            grid_lines.append(line)
        
        return "\n".join(grid_lines)
    
    def render_sidebar(self) -> Panel:
        """
        Render the sidebar panel with stats.
        
        Returns:
            Rich Panel with game statistics
        """
        if not self.game_state:
            return Panel("No game state")
        
        x, y = self.game_state.robot_pos
        metrics = self.game_state.metrics
        
        sidebar_content = (
            "[bold cyan]📍 CURRENT POSITION[/bold cyan]\n"
            f"X: {x:2d}  Y: {y:2d}\n\n"
            
            "[bold yellow]👣 MOVEMENT[/bold yellow]\n"
            f"Total Steps: {self.game_state.steps}\n"
            f"Path Length: {metrics.path_length}\n\n"
            
            "[bold magenta]📊 COMPUTATIONAL STATS[/bold magenta]\n"
            f"Nodes Explored: {metrics.nodes_explored}\n"
            f"Efficiency: {metrics.efficiency:.2f}%\n"
            f"Time: {metrics.computation_time_ms:.2f}ms\n\n"
            
            "[bold green]🎯 STATUS[/bold green]\n"
        )
        
        if self.game_state.is_finished:
            sidebar_content += "[green]✓ GOAL REACHED![/green]"
        else:
            progress = (self.game_state.current_path_index / max(metrics.path_length, 1)) * 100
            sidebar_content += f"Progress: {progress:.0f}%"
        
        return Panel(sidebar_content, border_style="blue", padding=(1, 1))
    
    def render_display(self) -> Layout:
        """
        Create the main display layout.
        
        Returns:
            Rich Layout object combining grid and sidebar
        """
        layout = Layout()
        layout.split_row(
            Layout(name="grid"),
            Layout(name="sidebar", size=30)
        )
        
        # Grid panel
        grid_content = Panel(
            self.render_grid(),
            title="[bold]Game Grid[/bold]",
            border_style="cyan",
            padding=(0, 1)
        )
        layout["grid"].update(grid_content)
        
        # Sidebar panel
        layout["sidebar"].update(self.render_sidebar())
        
        return layout
    
    def run_animation(self) -> None:
        """Run the main animation loop"""
        if not self.game_state or not self.config:
            return
        
        self.console.clear()
        
        # Live display
        with Live(self.render_display(), refresh_per_second=10, console=self.console) as live:
            # Initial reveal around start
            self.fog_of_war.reveal_around(*self.grid.start_pos)
            self.game_state.discovered_tiles = self.fog_of_war.discovered_tiles.copy()
            
            # Animation loop
            while not self.game_state.is_finished:
                # Update display
                live.update(self.render_display())
                
                # Move robot
                self.game_state.move_to_next()
                
                # Reveal tiles around robot
                if not self.game_state.is_finished:
                    self.fog_of_war.reveal_around(*self.game_state.robot_pos)
                    self.game_state.discovered_tiles = self.fog_of_war.discovered_tiles.copy()
                
                # Sleep based on animation speed
                time.sleep(self.config.speed.value)
            
            # Final update
            live.update(self.render_display())
        
        # Show completion message
        self.console.print("\n")
        completion_panel = Panel(
            "[bold green]🎉 GOAL REACHED! 🎉[/bold green]\n"
            f"[yellow]Total Steps: {self.game_state.steps}[/yellow]\n"
            f"[cyan]Path Length: {self.game_state.metrics.path_length}[/cyan]\n"
            f"[magenta]Nodes Explored: {self.game_state.metrics.nodes_explored}[/magenta]\n"
            f"[blue]Efficiency: {self.game_state.metrics.efficiency:.2f}%[/blue]\n"
            f"[green]Computation Time: {self.game_state.metrics.computation_time_ms:.2f}ms[/green]",
            border_style="green",
            padding=(1, 2)
        )
        self.console.print(completion_panel)
    
    def run(self) -> None:
        """Main entry point"""
        try:
            # Show menu and get config
            config = self.show_main_menu()
            self.console.print()
            
            # Initialize game
            self.initialize_game(config)
            
            # Validate path exists
            if not self.game_state.path:
                self.console.print("[red]❌ No valid path found![/red]")
                return
            
            self.console.print(f"[green]✓ Path found with {len(self.game_state.path)} steps![/green]")
            self.console.print("[yellow]Press Enter to start animation...[/yellow]")
            input()
            
            # Run animation
            self.run_animation()
            
            # Ask to play again
            self.console.print()
            if Confirm.ask("[bold]Play again?[/bold]", default=True):
                self.run()
            else:
                self.console.print("[cyan]👋 Thanks for playing![/cyan]")
        
        except KeyboardInterrupt:
            self.console.print("\n[yellow]⏹️ Game interrupted by user[/yellow]")
        except Exception as e:
            self.console.print(f"[red]❌ Error: {e}[/red]")


# ============================================================================
# ENTRY POINT
# ============================================================================

def main():
    """Entry point for the application"""
    navigator = Navigator()
    navigator.run()


if __name__ == "__main__":
    main()
