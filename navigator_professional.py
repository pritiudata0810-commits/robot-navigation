"""
GRID-BASED ROBOT NAVIGATION WITH OBSTACLE AVOIDANCE
Professional AI Simulation Dashboard

A high-tech TUI simulation using Rich library featuring:
- Dynamic random grid generation based on difficulty
- A* pathfinding algorithm (AI-powered navigation)
- 3-column professional dashboard layout
- Real-time telemetry and live move logs
- Clean, professional cyberpunk-inspired UI
"""

import random
import time
from typing import List, Tuple, Set, Optional
from dataclasses import dataclass, field
from enum import Enum
import heapq
from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich.columns import Columns
from rich.align import Align


# ============================================================================
# ENUMS & CONFIGURATION
# ============================================================================

class Difficulty(Enum):
    """Grid difficulty levels with wall percentages"""
    SLOW = 0.10    # 10% walls
    MEDIUM = 0.25  # 25% walls
    HARD = 0.40    # 40% walls


class Speed(Enum):
    """Animation speed settings (delay between moves in ms)"""
    SLOW = 200
    NORMAL = 100
    FAST = 50


# ============================================================================
# THEME & STYLING
# ============================================================================

class ProfessionalTheme:
    """Professional cyberpunk color palette"""
    CYAN = "#00FFFF"
    MAGENTA = "#FF00FF"
    DARK_BLUE = "#001133"
    NEON_GREEN = "#00FF00"
    WHITE = "#FFFFFF"
    RED = "#FF0000"
    YELLOW = "#FFFF00"


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class GridConfig:
    """Configuration for grid generation"""
    size: int = 12
    difficulty: Difficulty = Difficulty.MEDIUM
    
    def get_wall_count(self) -> int:
        """Calculate number of walls based on difficulty"""
        total_tiles = self.size * self.size
        wall_percentage = self.difficulty.value
        return int(total_tiles * wall_percentage)


@dataclass
class Point:
    """Represents a 2D point on the grid"""
    x: int
    y: int
    
    def __hash__(self):
        return hash((self.x, self.y))
    
    def __eq__(self, other):
        if isinstance(other, Point):
            return self.x == other.x and self.y == other.y
        return False


@dataclass
class SimulationState:
    """Current state of the simulation"""
    robot_pos: Point = field(default_factory=lambda: Point(0, 0))
    current_step: int = 0
    total_steps: int = 0
    move_log: List[str] = field(default_factory=list)
    elapsed_time: float = 0.0
    is_finished: bool = False
    path_taken: List[Point] = field(default_factory=list)


# ============================================================================
# GRID MANAGEMENT
# ============================================================================

class NavigationGrid:
    """Manages the grid, obstacles, and pathfinding"""
    
    def __init__(self, config: GridConfig):
        self.config = config
        self.size = config.size
        self.grid = [[False for _ in range(self.size)] for _ in range(self.size)]
        self.start = Point(0, 0)
        self.goal = Point(self.size - 1, self.size - 1)
        self.path: List[Point] = []
        self._generate_grid()
    
    def _generate_grid(self) -> None:
        """Generate random grid with walls based on difficulty"""
        wall_count = self.config.get_wall_count()
        
        # Reserve start and goal positions
        reserved = {(self.start.x, self.start.y), (self.goal.x, self.goal.y)}
        
        placed_walls = 0
        attempts = 0
        max_attempts = wall_count * 3
        
        while placed_walls < wall_count and attempts < max_attempts:
            x = random.randint(0, self.size - 1)
            y = random.randint(0, self.size - 1)
            
            if (x, y) not in reserved and not self.grid[y][x]:
                self.grid[y][x] = True
                
                # Validate path still exists
                if self._has_valid_path():
                    placed_walls += 1
                else:
                    # Undo if it blocks the path
                    self.grid[y][x] = False
            
            attempts += 1
    
    def _has_valid_path(self) -> bool:
        """Check if a valid path exists using BFS"""
        from collections import deque
        visited = {(self.start.x, self.start.y)}
        queue = deque([(self.start.x, self.start.y)])
        
        while queue:
            x, y = queue.popleft()
            
            if x == self.goal.x and y == self.goal.y:
                return True
            
            for nx, ny in self._get_neighbors(x, y):
                if (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append((nx, ny))
        
        return False
    
    def _get_neighbors(self, x: int, y: int) -> List[Tuple[int, int]]:
        """Get valid neighboring cells (4-directional movement)"""
        neighbors = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.size and 0 <= ny < self.size and not self.grid[ny][nx]:
                neighbors.append((nx, ny))
        return neighbors
    
    def calculate_path_astar(self) -> List[Point]:
        """Calculate optimal path using A* algorithm"""
        def heuristic(pos: Tuple[int, int]) -> int:
            """Manhattan distance heuristic"""
            return abs(pos[0] - self.goal.x) + abs(pos[1] - self.goal.y)
        
        open_set = []
        heapq.heappush(open_set, (0, (self.start.x, self.start.y)))
        
        came_from = {}
        g_score = {(self.start.x, self.start.y): 0}
        f_score = {(self.start.x, self.start.y): heuristic((self.start.x, self.start.y))}
        
        closed_set = set()
        
        while open_set:
            _, current = heapq.heappop(open_set)
            
            if current == (self.goal.x, self.goal.y):
                # Reconstruct path
                path = [Point(self.goal.x, self.goal.y)]
                while current in came_from:
                    current = came_from[current]
                    path.append(Point(current[0], current[1]))
                return list(reversed(path))
            
            closed_set.add(current)
            
            for neighbor in self._get_neighbors(current[0], current[1]):
                if neighbor in closed_set:
                    continue
                
                tentative_g = g_score[current] + 1
                
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f = tentative_g + heuristic(neighbor)
                    f_score[neighbor] = f
                    heapq.heappush(open_set, (f, neighbor))
        
        return []  # No path found
    
    def is_wall(self, x: int, y: int) -> bool:
        """Check if a cell contains a wall"""
        return self.grid[y][x] if 0 <= x < self.size and 0 <= y < self.size else False


# ============================================================================
# UI RENDERING
# ============================================================================

class DashboardRenderer:
    """Renders the professional 3-column dashboard"""
    
    def __init__(self):
        self.console = Console()
    
    def render_live_logs(self, state: SimulationState, max_visible: int = 8) -> Panel:
        """Render the live logs panel (left column)"""
        log_text = Text()
        log_text.append("LIVE LOGS\n", style=f"bold {ProfessionalTheme.CYAN}")
        log_text.append("─" * 30 + "\n", style=ProfessionalTheme.MAGENTA)
        
        # Show last N moves
        visible_logs = state.move_log[-max_visible:]
        if visible_logs:
            for log_entry in visible_logs:
                log_text.append(log_entry + "\n", style=ProfessionalTheme.NEON_GREEN)
        else:
            log_text.append("[dim]Awaiting simulation start...[/dim]\n")
        
        return Panel(
            log_text,
            border_style=ProfessionalTheme.CYAN,
            padding=(1, 2),
            expand=False,
            width=35
        )
    
    def render_navigation_grid(self, grid: NavigationGrid, state: SimulationState) -> Panel:
        """Render the main navigation grid (middle column)"""
        grid_text = Text()
        grid_text.append("NAVIGATION GRID\n", style=f"bold {ProfessionalTheme.MAGENTA}")
        grid_text.append("─" * 30 + "\n", style=ProfessionalTheme.DARK_BLUE)
        
        # Build grid display
        path_set = set(state.path_taken)
        
        for y in range(grid.size):
            for x in range(grid.size):
                current_pos = Point(x, y)
                
                if current_pos == grid.start:
                    grid_text.append("🤖 ", style=ProfessionalTheme.CYAN)
                elif current_pos == state.robot_pos:
                    grid_text.append("⭐ ", style=ProfessionalTheme.YELLOW)
                elif current_pos == grid.goal:
                    grid_text.append("🎯 ", style=ProfessionalTheme.RED)
                elif grid.is_wall(x, y):
                    grid_text.append("🧱 ", style=ProfessionalTheme.WHITE)
                elif current_pos in path_set:
                    grid_text.append("🟩 ", style=ProfessionalTheme.NEON_GREEN)
                else:
                    grid_text.append("  ", style="dim")
            
            grid_text.append("\n")
        
        return Panel(
            grid_text,
            border_style=ProfessionalTheme.MAGENTA,
            padding=(1, 1),
            expand=True
        )
    
    def render_telemetry(self, state: SimulationState, speed: Speed) -> Panel:
        """Render telemetry panel (right column)"""
        telemetry_text = Text()
        telemetry_text.append("TELEMETRY\n", style=f"bold {ProfessionalTheme.NEON_GREEN}")
        telemetry_text.append("─" * 25 + "\n", style=ProfessionalTheme.MAGENTA)
        
        telemetry_text.append("Position: ", style=ProfessionalTheme.CYAN)
        telemetry_text.append(f"X={state.robot_pos.x} Y={state.robot_pos.y}\n", style=ProfessionalTheme.WHITE)
        
        telemetry_text.append("Speed: ", style=ProfessionalTheme.CYAN)
        telemetry_text.append(f"{speed.name}\n", style=ProfessionalTheme.WHITE)
        
        telemetry_text.append("Elapsed Time: ", style=ProfessionalTheme.CYAN)
        telemetry_text.append(f"{state.elapsed_time:.2f}s\n", style=ProfessionalTheme.WHITE)
        
        telemetry_text.append("Current Move: ", style=ProfessionalTheme.CYAN)
        telemetry_text.append(f"#{state.current_step}\n", style=ProfessionalTheme.WHITE)
        
        telemetry_text.append("Total Moves: ", style=ProfessionalTheme.CYAN)
        telemetry_text.append(f"{state.total_steps}\n", style=ProfessionalTheme.WHITE)
        
        telemetry_text.append("\n[bold cyan]STATUS[/bold cyan]\n")
        if state.is_finished:
            telemetry_text.append("✓ GOAL REACHED", style=f"bold {ProfessionalTheme.NEON_GREEN}")
        else:
            telemetry_text.append("▶ RUNNING...", style=f"bold {ProfessionalTheme.YELLOW}")
        
        return Panel(
            telemetry_text,
            border_style=ProfessionalTheme.NEON_GREEN,
            padding=(1, 2),
            expand=False,
            width=35
        )
    
    def render_dashboard(self, grid: NavigationGrid, state: SimulationState, speed: Speed) -> Layout:
        """Render complete 3-column dashboard"""
        layout = Layout()
        layout.split_row(
            Layout(self.render_live_logs(state), name="left"),
            Layout(self.render_navigation_grid(grid, state), name="middle"),
            Layout(self.render_telemetry(state, speed), name="right")
        )
        return layout
    
    def render_mission_success(self, grid: NavigationGrid, state: SimulationState, 
                               speed: Speed, difficulty: Difficulty) -> None:
        """Display final mission success screen"""
        self.console.clear()
        
        # Title
        title = Text()
        title.append("GRID-BASED ROBOT NAVIGATION\nWITH OBSTACLE AVOIDANCE\n", 
                     style=f"bold {ProfessionalTheme.MAGENTA}")
        self.console.print(title, justify="center")
        
        # Stats table
        table = Table(title="[bold cyan]MISSION SUMMARY[/bold cyan]", 
                     show_header=True, header_style=ProfessionalTheme.CYAN,
                     border_style=ProfessionalTheme.MAGENTA)
        table.add_column("Metric", style=ProfessionalTheme.CYAN)
        table.add_column("Value", style=ProfessionalTheme.WHITE)
        
        table.add_row("Difficulty Level", difficulty.name)
        table.add_row("Movement Speed", speed.name)
        table.add_row("Steps Taken", str(state.total_steps))
        table.add_row("Grid Size", f"{grid.size}×{grid.size}")
        table.add_row("Elapsed Time", f"{state.elapsed_time:.2f}s")
        
        self.console.print(table)
        
        # Path summary
        self.console.print(f"\n[bold cyan]PATH SUMMARY[/bold cyan]", justify="center")
        self.console.print(f"[{ProfessionalTheme.NEON_GREEN}]Robot navigated from start (🤖) to goal (🎯) using A* pathfinding algorithm[/]")
        
        # Final grid snapshot
        self.console.print(f"\n[bold cyan]FINAL GRID STATE[/bold cyan]")
        grid_text = Text()
        for y in range(grid.size):
            for x in range(grid.size):
                current_pos = Point(x, y)
                
                if current_pos == grid.goal:
                    grid_text.append("🎯 ", style=ProfessionalTheme.RED)
                elif grid.is_wall(x, y):
                    grid_text.append("🧱 ", style=ProfessionalTheme.WHITE)
                elif current_pos in set(state.path_taken):
                    grid_text.append("🟩 ", style=ProfessionalTheme.NEON_GREEN)
                else:
                    grid_text.append("  ", style="dim")
            
            grid_text.append("\n")
        
        self.console.print(grid_text)
        
        # Termination message
        termination = Text()
        termination.append("SIMULATION TERMINATED: GOAL REACHED\n", 
                          style=f"bold {ProfessionalTheme.NEON_GREEN}")
        self.console.print(termination, justify="center")


# ============================================================================
# MENU SYSTEM
# ============================================================================

class MenuSystem:
    """Interactive selection menus"""
    
    @staticmethod
    def select_difficulty() -> Difficulty:
        """Menu to select difficulty level"""
        console = Console()
        console.clear()
        
        title = Text("SELECT DIFFICULTY LEVEL", style=f"bold {ProfessionalTheme.CYAN}")
        console.print(title, justify="center")
        console.print()
        
        options = [
            ("1", "SLOW (10% walls)", Difficulty.SLOW),
            ("2", "MEDIUM (25% walls)", Difficulty.MEDIUM),
            ("3", "HARD (40% walls)", Difficulty.HARD),
        ]
        
        for key, label, _ in options:
            console.print(f"  [{ProfessionalTheme.MAGENTA}]{key}[/]  {label}")
        
        console.print()
        while True:
            choice = console.input(f"[{ProfessionalTheme.CYAN}]Enter choice (1-3): [/]").strip()
            for key, _, difficulty in options:
                if choice == key:
                    return difficulty
            console.print(f"[{ProfessionalTheme.RED}]Invalid choice. Please try again.[/]")
    
    @staticmethod
    def select_speed() -> Speed:
        """Menu to select animation speed"""
        console = Console()
        console.clear()
        
        title = Text("SELECT MOVEMENT SPEED", style=f"bold {ProfessionalTheme.MAGENTA}")
        console.print(title, justify="center")
        console.print()
        
        options = [
            ("1", "SLOW (200ms delay)", Speed.SLOW),
            ("2", "NORMAL (100ms delay)", Speed.NORMAL),
            ("3", "FAST (50ms delay)", Speed.FAST),
        ]
        
        for key, label, _ in options:
            console.print(f"  [{ProfessionalTheme.NEON_GREEN}]{key}[/]  {label}")
        
        console.print()
        while True:
            choice = console.input(f"[{ProfessionalTheme.CYAN}]Enter choice (1-3): [/]").strip()
            for key, _, speed in options:
                if choice == key:
                    return speed
            console.print(f"[{ProfessionalTheme.RED}]Invalid choice. Please try again.[/]")


# ============================================================================
# MAIN SIMULATOR
# ============================================================================

class RobotNavigationSimulator:
    """Main simulation engine"""
    
    def __init__(self):
        self.console = Console()
        self.renderer = DashboardRenderer()
    
    def run(self) -> None:
        """Execute the full simulation"""
        # Select parameters
        difficulty = MenuSystem.select_difficulty()
        speed = MenuSystem.select_speed()
        
        # Initialize
        config = GridConfig(size=12, difficulty=difficulty)
        grid = NavigationGrid(config)
        state = SimulationState()
        state.robot_pos = grid.start
        
        # Pre-simulation screen
        self.console.clear()
        
        info_text = Text()
        info_text.append("GRID GENERATED\n", style=f"bold {ProfessionalTheme.CYAN}")
        info_text.append(f"Size: {grid.size}×{grid.size}\n", style=ProfessionalTheme.WHITE)
        info_text.append(f"Difficulty: {difficulty.name}\n", style=ProfessionalTheme.WHITE)
        info_text.append(f"Speed: {speed.name}\n\n", style=ProfessionalTheme.WHITE)
        info_text.append("Press ENTER to calculate path and start simulation...", 
                        style=f"bold {ProfessionalTheme.NEON_GREEN}")
        
        self.console.print(Align.center(info_text))
        input()  # Wait for user to press Enter
        
        # Calculate path using A*
        self.console.clear()
        wait_text = Text("Calculating optimal path using A* algorithm...", 
                        style=f"bold {ProfessionalTheme.YELLOW}")
        self.console.print(Align.center(wait_text))
        time.sleep(0.5)
        
        grid.path = grid.calculate_path_astar()
        
        if not grid.path:
            error = Text("ERROR: No path found!", style=f"bold {ProfessionalTheme.RED}")
            self.console.print(Align.center(error))
            return
        
        state.total_steps = len(grid.path) - 1
        
        # Run animation
        self._run_animation(grid, state, speed)
        
        # Show success screen
        self.renderer.render_mission_success(grid, state, speed, difficulty)
    
    def _run_animation(self, grid: NavigationGrid, state: SimulationState, speed: Speed) -> None:
        """Animate the robot following the path"""
        self.console.clear()
        
        # Direction mapping for logging
        direction_map = {
            (-1, 0): "left",
            (1, 0): "right",
            (0, -1): "up",
            (0, 1): "down"
        }
        
        start_time = time.time()
        
        with Live(self.renderer.render_dashboard(grid, state, speed), 
                 console=self.console, refresh_per_second=10):
            
            for i, next_pos in enumerate(grid.path[1:], 1):
                state.current_step = i
                prev_pos = state.robot_pos
                state.robot_pos = next_pos
                state.path_taken.append(next_pos)
                
                # Log the move
                dx = next_pos.x - prev_pos.x
                dy = next_pos.y - prev_pos.y
                direction = direction_map.get((dx, dy), "unknown")
                move_log_entry = f"Move #{i}: {direction}"
                state.move_log.append(move_log_entry)
                
                # Update telemetry
                state.elapsed_time = time.time() - start_time
                
                # Wait for animation speed
                time.sleep(speed.value / 1000.0)
        
        state.is_finished = True


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    simulator = RobotNavigationSimulator()
    simulator.run()
