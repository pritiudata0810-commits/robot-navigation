"""
CYBERPUNK MISSION CONTROL DASHBOARD
Robot Navigation Simulator with A* Pathfinding & Fog of War
A professional TUI-based game using Rich library featuring:
- A* pathfinding with explored node tracking
- 3-column cyberpunk layout with real-time telemetry
- Neon color palette with 3-layer depth lighting
- Radar pulses, particle trails, and heatmap effects
- Dynamic hazards and A* search frontier visualization
- 50ms frame updates for smooth 20fps animation
"""

import random
import time
import math
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
from rich.text import Text
from rich.segment import Segment


# ============================================================================
# CYBERPUNK THEME & EFFECTS ENGINE
# ============================================================================

class CyberpunkTheme:
    """Neon color palette and visual effects configuration"""
    
    # Neon colors
    CYAN = "#00FFFF"
    MAGENTA = "#FF00FF"
    NEON_GREEN = "#00FF00"
    BRIGHT_BLUE = "#0088FF"
    DEEP_PURPLE = "#330033"
    DARK_BLUE = "#001133"
    RED_ALERT = "#FF0000"
    YELLOW_FLICKER = "#FFFF00"
    
    @staticmethod
    def depth_color(brightness_level: int) -> str:
        """Return color based on depth (0=bright neon, 1=dim blue, 2=deep purple)"""
        colors = ["#00FFFF", "#0066CC", "#330033"]
        return colors[min(brightness_level, 2)]
    
    @staticmethod
    def glow_char(char: str, intensity: int) -> str:
        """Apply color intensity to character (0-5 levels)"""
        if intensity == 0:
            return f"[dim]{char}[/dim]"
        elif intensity < 3:
            return f"[{CyberpunkTheme.DARK_BLUE}]{char}[/{CyberpunkTheme.DARK_BLUE}]"
        else:
            return f"[{CyberpunkTheme.CYAN}]{char}[/{CyberpunkTheme.CYAN}]"


@dataclass
class AnimationState:
    """Track animation frame state for effects"""
    frame_count: int = 0
    pulse_radius: float = 0.0
    flicker_state: bool = False
    scanline_offset: int = 0
    time_ms: float = 0.0
    
    def tick(self, dt_ms: float = 50) -> None:
        """Advance animation by one frame"""
        self.frame_count += 1
        self.time_ms += dt_ms
        self.pulse_radius = (self.frame_count % 20) / 5.0
        self.flicker_state = (self.frame_count // 5) % 2 == 0
        self.scanline_offset = self.frame_count % 4


@dataclass
class Hazard:
    """Dynamic moving hazard with collision detection"""
    x: float
    y: float
    vx: float
    vy: float
    active: bool = True
    
    def update(self, grid_size: int) -> None:
        """Update hazard position with boundary wrapping"""
        self.x += self.vx
        self.y += self.vy
        
        # Bounce off boundaries
        if self.x < 0 or self.x >= grid_size:
            self.vx *= -1
            self.x = max(0, min(grid_size - 1, self.x))
        if self.y < 0 or self.y >= grid_size:
            self.vy *= -1
            self.y = max(0, min(grid_size - 1, self.y))
    
    def distance_to(self, x: int, y: int) -> float:
        """Calculate distance to a position"""
        return math.sqrt((self.x - x) ** 2 + (self.y - y) ** 2)


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
    """Main game controller and UI renderer with cyberpunk effects"""
    
    def __init__(self):
        self.console = Console()
        self.config: Optional[GameConfig] = None
        self.grid: Optional[Grid] = None
        self.game_state: Optional[GameState] = None
        self.astar: Optional[AStar] = None
        self.fog_of_war: Optional[FogOfWar] = None
        self.animation_state = AnimationState()
        self.hazards: List[Hazard] = []
        self.particle_trails: Dict[Tuple[int, int], int] = {}  # pos -> age
        self.heatmap: Dict[Tuple[int, int], int] = {}  # pos -> intensity (0-5)
        self.hex_stream: List[str] = []
        self.search_frontier: Set[Tuple[int, int]] = set()
        self.last_frame_time = time.time()
    
    def show_main_menu(self) -> GameConfig:
        """Display cyberpunk-themed main menu and get user selections"""
        self.console.clear()
        
        # Cyberpunk welcome banner
        banner = Panel(
            "[bold #00FFFF]⚡ MISSION CONTROL OVERRIDE ⚡[/bold #00FFFF]\n"
            "[#FF00FF]CYBERPUNK NAVIGATION SYSTEM[/#FF00FF]\n"
            "[dim #0088FF]A* Pathfinding with Fog of War[/dim #0088FF]",
            border_style="#00FFFF",
            padding=(1, 2),
            expand=False
        )
        self.console.print(banner)
        self.console.print()
        
        # Difficulty selection
        difficulty_panel = Panel(
            "[bold #00FF00]< DIFFICULTY CONFIGURATION >[/bold #00FF00]\n"
            "[cyan]Easy[/cyan]     → 10% walls\n"
            "[yellow]Medium[/yellow]  → 25% walls\n"
            "[#FF0000]Hard[/#FF0000]     → 40% walls",
            border_style="#00FF00",
            padding=(1, 2)
        )
        self.console.print(difficulty_panel)
        
        difficulty_input = Prompt.ask(
            "[bold #00FFFF]DIFFICULTY[/bold #00FFFF]",
            choices=["easy", "medium", "hard"],
            default="medium"
        ).lower()
        
        difficulty_map = {
            "easy": Difficulty.EASY,
            "medium": Difficulty.MEDIUM,
            "hard": Difficulty.HARD
        }
        selected_difficulty = difficulty_map[difficulty_input]
        self.console.print(f"[#00FF00]✓ {selected_difficulty.name.upper()}[/#00FF00]")
        self.console.print()
        
        # Speed selection
        speed_panel = Panel(
            "[bold #FF00FF]< ANIMATION SPEED >[/bold #FF00FF]\n"
            "[cyan]Slow[/cyan]    → 1.0s per step\n"
            "[yellow]Normal[/yellow]  → 0.5s per step\n"
            "[#00FF00]Fast[/#00FF00]   → 0.2s per step",
            border_style="#FF00FF",
            padding=(1, 2)
        )
        self.console.print(speed_panel)
        
        speed_input = Prompt.ask(
            "[bold #00FFFF]SPEED[/bold #00FFFF]",
            choices=["slow", "normal", "fast"],
            default="normal"
        ).lower()
        
        speed_map = {
            "slow": Speed.SLOW,
            "normal": Speed.NORMAL,
            "fast": Speed.FAST
        }
        selected_speed = speed_map[speed_input]
        self.console.print(f"[#00FF00]✓ {selected_speed.name.upper()}[/#00FF00]")
        self.console.print()
        
        self.console.print("[bold #FF00FF]>> INITIALIZING MISSION CONTROL <<[/bold #FF00FF]")
        
        return GameConfig(difficulty=selected_difficulty, speed=selected_speed)
    
    def initialize_game(self, config: GameConfig) -> None:
        """Initialize grid, pathfinding, game state, and cyberpunk effects"""
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
        
        # Initialize cyberpunk effects
        self.animation_state = AnimationState()
        self._spawn_hazards()
        self.particle_trails = {}
        self.heatmap = {}
        self.hex_stream = []
        # Get explored nodes from metrics
        self.search_frontier = self.game_state.metrics.explored_nodes.copy()
    
    def _spawn_hazards(self) -> None:
        """Create 3 moving hazards at random positions"""
        self.hazards = []
        for _ in range(3):
            while True:
                x = random.randint(2, self.grid.size - 2)
                y = random.randint(2, self.grid.size - 2)
                if (x, y) not in [self.grid.start_pos, self.grid.goal_pos]:
                    break
            
            # Random velocities
            vx = random.choice([-0.3, -0.1, 0.1, 0.3])
            vy = random.choice([-0.3, -0.1, 0.1, 0.3])
            self.hazards.append(Hazard(float(x), float(y), vx, vy))
    
    def render_grid(self) -> str:
        """
        Render the 20x20 game grid with cyberpunk effects:
        - Neon glow heatmap
        - Radar pulse circles
        - Particle trails
        - A* search frontier
        - Hazards and scanlines
        """
        if not self.grid or not self.game_state:
            return ""
        
        grid_lines = []
        rx, ry = self.game_state.robot_pos
        
        # Scanline for cyberpunk effect
        scanline = "▒" if self.animation_state.scanline_offset % 2 == 0 else " "
        
        for y in range(self.grid.size):
            line = ""
            for x in range(self.grid.size):
                pos = (x, y)
                
                # Calculate glow intensity from heatmap
                glow_intensity = self.heatmap.get(pos, 0)
                
                # Radar pulse effect
                in_pulse = False
                if self.animation_state.pulse_radius > 0:
                    dist = math.sqrt((x - rx) ** 2 + (y - ry) ** 2)
                    if abs(dist - self.animation_state.pulse_radius) < 1.5:
                        in_pulse = True
                
                # Determine what to render
                char = " "
                style = ""
                
                # Robot
                if pos == self.game_state.robot_pos:
                    char = "🤖"
                    style = "bold #00FFFF"
                # Goal
                elif pos == self.grid.goal_pos:
                    char = "🏁"
                    style = "bold #FF00FF"
                # Hazards
                elif any(int(h.x) == x and int(h.y) == y for h in self.hazards):
                    char = "✕"
                    style = "bold #FF0000"
                # Wall
                elif self.grid.grid[y][x]:
                    if pos in self.game_state.discovered_tiles:
                        char = "█"
                        style = "#0088FF"
                    else:
                        char = "·"
                        style = "dim"
                # Particle trail
                elif pos in self.particle_trails:
                    trail_age = self.particle_trails[pos]
                    particles = ["⚡", "¤", "·"]
                    char = particles[trail_age % 3]
                    intensity = max(0, 3 - (trail_age // 2))
                    if intensity > 0:
                        style = f"{CyberpunkTheme.depth_color(min(intensity, 2))}"
                # A* search frontier (flickering yellow)
                elif pos in self.search_frontier and self.animation_state.flicker_state:
                    char = "·"
                    style = "#FFFF00 dim"
                # Explored nodes
                elif pos in self.game_state.metrics.explored_nodes:
                    if pos in self.game_state.discovered_tiles:
                        char = "·"
                        if glow_intensity > 0:
                            style = f"{CyberpunkTheme.depth_color(glow_intensity - 1)}"
                        else:
                            style = "dim #0088FF"
                    else:
                        char = "·"
                        style = "dim"
                # Regular path
                else:
                    if pos in self.game_state.discovered_tiles:
                        char = "·"
                        if glow_intensity > 0:
                            style = f"{CyberpunkTheme.depth_color(glow_intensity - 1)}"
                        else:
                            style = "dim #00FFFF"
                    else:
                        char = "·"
                        style = "dim"
                
                # Apply radar pulse highlight
                if in_pulse and char != "🤖" and char != "🏁":
                    style = "bold #00FFFF"
                
                # Apply style
                if style:
                    line += f"[{style}]{char}[/{style.split()[0]}]"
                else:
                    line += char
                
                # Scanline overlay
                if y % 3 == 0:
                    line += scanline
            
            grid_lines.append(line)
        
        return "\n".join(grid_lines)
    
    def render_hex_stream(self) -> str:
        """Render scrolling hex-code sensor stream for left panel"""
        # Generate or rotate hex stream
        if len(self.hex_stream) < 10:
            for _ in range(10):
                hex_code = f"{random.randint(0, 255):02X}{random.randint(0, 255):02X}{random.randint(0, 255):02X}"
                self.hex_stream.append(hex_code)
        
        # Rotate stream every few frames
        if self.animation_state.frame_count % 3 == 0 and len(self.hex_stream) > 0:
            self.hex_stream.pop(0)
            hex_code = f"{random.randint(0, 255):02X}{random.randint(0, 255):02X}{random.randint(0, 255):02X}"
            self.hex_stream.append(hex_code)
        
        # Display last 8 lines
        stream_lines = self.hex_stream[-8:]
        return "\n".join([f"[#00FFFF]{h}[/#00FFFF]" for h in stream_lines])
    
    def render_bar_charts(self) -> str:
        """Render ASCII bar charts for right panel"""
        if not self.game_state:
            return ""
        
        x, y = self.game_state.robot_pos
        metrics = self.game_state.metrics
        progress = (self.game_state.current_path_index / max(metrics.path_length, 1)) * 100 if metrics.path_length > 0 else 0
        
        # Bar chart for progress
        bar_width = 12
        filled = int((progress / 100) * bar_width)
        progress_bar = "█" * filled + "░" * (bar_width - filled)
        
        # Nodes explored normalized bar
        nodes_max = max(1, metrics.nodes_explored)
        explored_bar = "▓" * min(12, (metrics.nodes_explored // max(1, nodes_max // 12)))
        
        # Efficiency bar
        eff_bar = "▒" * min(12, int(metrics.efficiency / 10))
        
        content = (
            f"[#00FF00]PROGRESS[/#00FF00]\n"
            f"[#00FFFF]{progress_bar}[/#00FFFF] {progress:.0f}%\n\n"
            f"[#FF00FF]NODES[/#FF00FF]\n"
            f"[#FF00FF]{explored_bar}[/#FF00FF] {metrics.nodes_explored}\n\n"
            f"[#0088FF]EFFICIENCY[/#0088FF]\n"
            f"[#0088FF]{eff_bar}[/#0088FF] {metrics.efficiency:.1f}%"
        )
        
        return content
    
    def render_telemetry_bar(self) -> str:
        """Render top telemetry bar with status info"""
        # Satellite link status
        link_status = "STABLE" if self.animation_state.flicker_state else "SIGNAL"
        cpu_load = min(100, 30 + (self.animation_state.frame_count % 30))
        
        # Check for hazard alerts
        hazard_alert = ""
        rx, ry = self.game_state.robot_pos
        for hazard in self.hazards:
            if hazard.distance_to(rx, ry) < 4:
                if self.animation_state.flicker_state:
                    hazard_alert = " [bold #FF0000]⚠ RED ALERT ⚠[/bold #FF0000]"
                break
        
        # Coordinate mapping progress
        coord_progress = (self.animation_state.frame_count % 20) / 20
        coord_bar = "▓" * int(coord_progress * 10) + "░" * (10 - int(coord_progress * 10))
        
        telemetry = (
            f"[#00FFFF]▐ SATELLITE LINK: {link_status}[/#00FFFF] │ "
            f"[#FF00FF]CPU: {cpu_load}%[/#FF00FF] │ "
            f"[#00FF00]COORD [{coord_bar}][/#00FF00]{hazard_alert}"
        )
        
        return telemetry
    
    def render_sidebar(self) -> Panel:
        """Render right panel with statistics and charts"""
        if not self.game_state:
            return Panel("No game state")
        
        x, y = self.game_state.robot_pos
        metrics = self.game_state.metrics
        
        sidebar_content = (
            "[bold #FF00FF]< TELEMETRY >[/bold #FF00FF]\n"
            f"[#00FFFF]POS[/#00FFFF]: ({x:2d}, {y:2d})\n"
            f"[#00FFFF]STEPS[/#00FFFF]: {self.game_state.steps}/{metrics.path_length}\n"
            f"[#00FFFF]TIME[/#00FFFF]: {metrics.computation_time_ms:.1f}ms\n\n"
        )
        
        sidebar_content += self.render_bar_charts()
        
        return Panel(sidebar_content, border_style="#FF00FF", padding=(1, 1))
    
    def render_display(self) -> Layout:
        """
        Create the 3-column cyberpunk layout:
        Top: Telemetry bar
        Left: Hex Stream | Center: Grid | Right: Charts
        """
        # Main layout is 3-column: left, center, right
        layout = Layout()
        layout.split_row(
            Layout(name="left", size=18),
            Layout(name="center"),
            Layout(name="right", size=22)
        )
        
        # Left panel: Hex stream
        hex_panel = Panel(
            self.render_hex_stream(),
            title="[bold #00FFFF]HEX STREAM[/bold #00FFFF]",
            border_style="#00FFFF",
            padding=(0, 0)
        )
        layout["left"].update(hex_panel)
        
        # Center panel: Grid
        grid_content = Panel(
            self.render_grid(),
            title="[bold #00FF00]SECTOR MAP[/bold #00FF00]",
            border_style="#00FF00",
            padding=(0, 0)
        )
        layout["center"].update(grid_content)
        
        # Right panel: Stats and charts
        layout["right"].update(self.render_sidebar())
        
        return layout
    
    def _update_effects(self) -> None:
        """Update all animation effects each frame"""
        self.animation_state.tick(50)  # 50ms per frame
        
        # Update particle trails - age them
        aged_trails = []
        for pos, age in self.particle_trails.items():
            if age < 6:
                aged_trails.append((pos, age + 1))
        self.particle_trails = dict(aged_trails)
        
        # Update heatmap - fade intensity
        aged_heatmap = {}
        for pos, intensity in self.heatmap.items():
            if intensity > 0:
                aged_heatmap[pos] = intensity - 1
        self.heatmap = aged_heatmap
        
        # Update hazards
        for hazard in self.hazards:
            hazard.update(self.grid.size)
        
        # Add particle trail at robot position
        robot_pos = self.game_state.robot_pos
        if robot_pos not in self.particle_trails:
            self.particle_trails[robot_pos] = 0
        
        # Update heatmap around previous positions
        for explored_pos in self.game_state.metrics.explored_nodes:
            if explored_pos not in self.heatmap:
                self.heatmap[explored_pos] = 5
    
    def run_animation(self) -> None:
        """
        Run the main animation loop with 0.05s (50ms) frame updates.
        Includes telemetry bar, hazard updates, and effect animations.
        """
        if not self.game_state or not self.config:
            return
        
        self.console.clear()
        
        # Use 0.05s frame timing (20fps equivalent)
        frame_delay = 0.05
        
        # Create a wrapper renderfunction to include telemetry
        def render_with_telemetry():
            """Render layout with telemetry bar on top"""
            layout = Layout()
            layout.split_column(
                Layout(Panel(self.render_telemetry_bar(), border_style="#FF00FF", padding=(0, 1)), size=3),
                Layout(self.render_display())
            )
            return layout
        
        # Live display with high refresh rate
        with Live(render_with_telemetry(), refresh_per_second=20, console=self.console) as live:
            # Initial reveal around start
            self.fog_of_war.reveal_around(*self.grid.start_pos)
            self.game_state.discovered_tiles = self.fog_of_war.discovered_tiles.copy()
            
            # Animation loop
            while not self.game_state.is_finished:
                frame_start = time.time()
                
                # Update effects and hazards
                self._update_effects()
                
                # Update display
                live.update(render_with_telemetry())
                
                # Move robot
                self.game_state.move_to_next()
                
                # Reveal tiles around robot
                if not self.game_state.is_finished:
                    self.fog_of_war.reveal_around(*self.game_state.robot_pos)
                    self.game_state.discovered_tiles = self.fog_of_war.discovered_tiles.copy()
                
                # Maintain frame rate
                elapsed = time.time() - frame_start
                move_delay = self.config.speed.value
                
                # Inter-frame updates (for smooth animation between moves)
                remaining_delay = move_delay - elapsed
                frames_in_move = max(1, int(remaining_delay / frame_delay))
                
                for _ in range(frames_in_move):
                    frame_start = time.time()
                    self._update_effects()
                    live.update(render_with_telemetry())
                    
                    frame_elapsed = time.time() - frame_start
                    if frame_elapsed < frame_delay:
                        time.sleep(frame_delay - frame_elapsed)
            
            # Final update and celebration
            live.update(render_with_telemetry())
        
        # Show cyberpunk success celebration
        self._show_success_celebration()
    
    def _show_success_celebration(self) -> None:
        """Display full-screen glitch-text success banner"""
        self.console.clear()
        
        # Create glitch effect with multiple colored layers
        glitch_lines = [
            "[bold #FF00FF]███████████████████████████████████[/bold #FF00FF]",
            "[bold #00FFFF]█                                   █[/bold #00FFFF]",
            "[bold #FF00FF]█  ███████╗██╗   ██╗███████╗████████╗█[/bold #FF00FF]",
            "[bold #00FF00]█  ██╔════╝╚██╗ ██╔╝██╔════╝╚══██╔══╝█[/bold #00FF00]",
            "[bold #00FFFF]█  ███████╗ ╚████╔╝ ███████╗   ██║   █[/bold #00FFFF]",
            "[bold #FF00FF]█  ╚════██║  ╚██╔╝  ╚════██║   ██║   █[/bold #FF00FF]",
            "[bold #00FF00]█  ███████║   ██║   ███████║   ██║   █[/bold #00FF00]",
            "[bold #00FFFF]█  ╚══════╝   ╚═╝   ╚══════╝   ╚═╝   █[/bold #00FFFF]",
            "[bold #FF00FF]█                                   █[/bold #FF00FF]",
            "[bold #00FFFF]█  [bold #00FF00]MISSION CONTROL CLEAR[/bold #00FF00]  █[/bold #00FFFF]",
            "[bold #FF00FF]█                                   █[/bold #FF00FF]",
            "[bold #00FFFF]███████████████████████████████████[/bold #00FFFF]",
        ]
        
        for line in glitch_lines:
            self.console.print(line, justify="center")
        
        self.console.print()
        
        # Mission summary table
        summary = Table(title="[bold #00FF00]MISSION SUMMARY[/bold #00FF00]", border_style="#FF00FF")
        summary.add_column("METRIC", style="#00FFFF")
        summary.add_column("VALUE", style="#00FF00")
        
        summary.add_row("Total Steps", str(self.game_state.steps))
        summary.add_row("Path Length", str(self.game_state.metrics.path_length))
        summary.add_row("Nodes Explored", str(self.game_state.metrics.nodes_explored))
        summary.add_row("Efficiency", f"{self.game_state.metrics.efficiency:.2f}%")
        summary.add_row("Computation Time", f"{self.game_state.metrics.computation_time_ms:.2f}ms")
        
        self.console.print(summary)
        self.console.print()
        self.console.print("[bold #00FF00]✓ MISSION OBJECTIVE COMPLETE ✓[/bold #00FF00]", justify="center")
    
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
