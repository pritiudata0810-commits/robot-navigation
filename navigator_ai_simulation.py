"""
GRID-BASED ROBOT NAVIGATION WITH A* PATHFINDING
Professional AI Simulation with Real-time Visualization

Installation requirement:
    pip install customtkinter

Run with:
    python navigator_ai_simulation.py
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import random
import time
import math
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional, Set
from collections import deque
from enum import Enum


# ============================================================================
# CONFIGURATION & CONSTANTS
# ============================================================================

class Difficulty(Enum):
    """Simulation difficulty levels"""
    EASY = 0.10
    MEDIUM = 0.25
    HARD = 0.40


class Speed(Enum):
    """Simulation speed settings"""
    SLOW = 500
    NORMAL = 200
    FAST = 50


# Color Scheme - Professional Robotics Theme
COLORS = {
    'bg_dark': '#0a0e27',           # Dark navy background
    'grid_bg': '#1a1f3a',           # Grid background
    'grid_cell_1': '#1a1f3a',       # Slightly different dark shade
    'grid_cell_2': '#1e2340',       # Alternating cell color
    'robot': '#00d4ff',             # Bright cyan/blue
    'goal': '#00ff41',              # Bright green
    'obstacle': '#2a2a2a',          # Dark grey
    'explored': '#00b8e6',          # Lighter cyan
    'path': '#ffff00',              # Yellow
    'empty': '#1a1f3a',             # Dark slate
    'panel_bg': '#141829',          # Panel background
    'text_primary': '#e0e0e0',      # Light grey text
    'text_secondary': '#a0a0a0',    # Medium grey text
    'accent': '#00d4ff',            # Accent color
}

GRID_SIZE = 20
CELL_SIZE = 25


# ============================================================================
# DATA STRUCTURES FOR A* ALGORITHM
# ============================================================================

@dataclass
class Node:
    """Represents a single node in the grid for A* pathfinding"""
    x: int
    y: int
    g_score: float = float('inf')  # Cost from start
    h_score: float = 0              # Heuristic (Manhattan distance to goal)
    
    @property
    def f_score(self) -> float:
        """Total cost estimate"""
        return self.g_score + self.h_score
    
    def __lt__(self, other):
        """For priority queue comparison"""
        return self.f_score < other.f_score
    
    def __eq__(self, other):
        """Equality check"""
        return self.x == other.x and self.y == other.y
    
    def __hash__(self):
        """For set operations"""
        return hash((self.x, self.y))


# ============================================================================
# GRID MANAGEMENT
# ============================================================================

class Grid:
    """Manages the grid, obstacles, and cell states"""
    
    def __init__(self, size: int = GRID_SIZE):
        self.size = size
        self.cells = [[0 for _ in range(size)] for _ in range(size)]  # 0 = empty
        self.robot_pos: Tuple[int, int] = (0, 0)
        self.goal_pos: Tuple[int, int] = (size - 1, size - 1)
        self.obstacles: Set[Tuple[int, int]] = set()
    
    def generate(self, difficulty: Difficulty):
        """
        Generate a new random grid with obstacles.
        0 = empty, 1 = obstacle
        """
        self.cells = [[0 for _ in range(self.size)] for _ in range(self.size)]
        self.obstacles = set()
        
        # Generate obstacles
        obstacle_density = difficulty.value
        num_obstacles = int(self.size * self.size * obstacle_density)
        
        for _ in range(num_obstacles):
            while True:
                x = random.randint(0, self.size - 1)
                y = random.randint(0, self.size - 1)
                # Don't place obstacle at corners or on each other
                if (x, y) not in [(0, 0), (self.size - 1, self.size - 1), (x, y) in self.obstacles]:
                    self.cells[y][x] = 1
                    self.obstacles.add((x, y))
                    break
        
        # Set robot and goal positions
        self.robot_pos = (0, 0)
        self.goal_pos = (self.size - 1, self.size - 1)
    
    def is_walkable(self, x: int, y: int) -> bool:
        """Check if a cell is walkable"""
        if x < 0 or x >= self.size or y < 0 or y >= self.size:
            return False
        return self.cells[y][x] == 0
    
    def get_neighbors(self, x: int, y: int) -> List[Tuple[int, int]]:
        """Get valid neighboring cells (4-directional movement)"""
        neighbors = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if self.is_walkable(nx, ny):
                neighbors.append((nx, ny))
        return neighbors
    
    def manhattan_distance(self, p1: Tuple[int, int], p2: Tuple[int, int]) -> float:
        """Calculate Manhattan distance between two points"""
        return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])


# ============================================================================
# A* PATHFINDING ALGORITHM
# ============================================================================

class AStarPathfinder:
    """Implements the A* pathfinding algorithm"""
    
    def __init__(self, grid: Grid):
        self.grid = grid
        self.explored_nodes: Set[Tuple[int, int]] = set()
        self.path: List[Tuple[int, int]] = []
        self.step_by_step: List[Tuple[int, int]] = []  # For visualization
    
    def find_path(self) -> Tuple[List[Tuple[int, int]], List[Tuple[int, int]]]:
        """
        Execute A* algorithm and return (path, explored_nodes)
        """
        start = self.grid.robot_pos
        goal = self.grid.goal_pos
        
        # Initialize
        open_set = {start}
        came_from: Dict[Tuple[int, int], Tuple[int, int]] = {}
        g_scores = {start: 0}
        h_scores = {start: self.grid.manhattan_distance(start, goal)}
        f_scores = {start: h_scores[start]}
        
        while open_set:
            # Find node with lowest f_score
            current = min(open_set, key=lambda p: f_scores.get(p, float('inf')))
            
            # Record exploration
            self.explored_nodes.add(current)
            self.step_by_step.append(current)
            
            if current == goal:
                # Reconstruct path
                path = [current]
                while current in came_from:
                    current = came_from[current]
                    path.append(current)
                path.reverse()
                self.path = path
                return path, list(self.explored_nodes)
            
            open_set.remove(current)
            
            for neighbor in self.grid.get_neighbors(current[0], current[1]):
                tentative_g = g_scores[current] + 1
                
                if neighbor not in g_scores or tentative_g < g_scores[neighbor]:
                    came_from[neighbor] = current
                    g_scores[neighbor] = tentative_g
                    h_scores[neighbor] = self.grid.manhattan_distance(neighbor, goal)
                    f_scores[neighbor] = g_scores[neighbor] + h_scores[neighbor]
                    
                    if neighbor not in open_set:
                        open_set.add(neighbor)
        
        # No path found
        return [], list(self.explored_nodes)


# ============================================================================
# ROBOT STATE MANAGEMENT
# ============================================================================

class Robot:
    """Manages the robot's position and movement"""
    
    def __init__(self, grid: Grid):
        self.grid = grid
        self.pos = grid.robot_pos
        self.path: List[Tuple[int, int]] = []
        self.current_path_index = 0
        self.total_steps = 0
    
    def set_path(self, path: List[Tuple[int, int]]):
        """Set the path for the robot to follow"""
        self.path = path
        self.current_path_index = 0
        self.total_steps = 0
    
    def move_along_path(self) -> bool:
        """
        Move robot one step along the path.
        Returns True if movement successful, False if path complete.
        """
        if self.current_path_index >= len(self.path) - 1:
            return False
        
        self.current_path_index += 1
        self.pos = self.path[self.current_path_index]
        self.total_steps += 1
        return True
    
    def is_at_goal(self) -> bool:
        """Check if robot reached the goal"""
        return self.pos == self.grid.goal_pos
    
    def reset(self):
        """Reset robot to start position"""
        self.pos = self.grid.robot_pos
        self.path = []
        self.current_path_index = 0
        self.total_steps = 0


# ============================================================================
# SIMULATION UI - MAIN APPLICATION
# ============================================================================

class SimulationUI:
    """Main UI class managing the simulation interface and logic"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Robot Navigation AI Simulator")
        self.root.geometry("1400x700")
        
        # Configure dark mode
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Simulation state
        self.grid = Grid()
        self.robot = Robot(self.grid)
        self.pathfinder = AStarPathfinder(self.grid)
        self.simulation_running = False
        self.animation_running = False
        self.difficulty = Difficulty.MEDIUM
        self.speed = Speed.NORMAL
        
        # Telemetry
        self.start_time = 0
        self.nodes_explored = 0
        
        # Layout
        self.setup_ui()
    
    def setup_ui(self):
        """Create the main UI layout"""
        self.root.configure(fg_color=COLORS['bg_dark'])
        
        # Main container
        main_frame = ctk.CTkFrame(self.root, fg_color=COLORS['bg_dark'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Left Panel - Controls
        self.left_panel = self.create_left_panel(main_frame)
        self.left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=10, pady=10, ipadx=5)
        
        # Center Panel - Grid Visualization
        self.center_panel = self.create_center_panel(main_frame)
        self.center_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=10)
        
        # Right Panel - Telemetry
        self.right_panel = self.create_right_panel(main_frame)
        self.right_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=10, pady=10, ipadx=5)
        
        # Initialize grid
        self.regenerate_grid()
    
    def create_left_panel(self, parent):
        """Create left control panel"""
        panel = ctk.CTkFrame(parent, fg_color=COLORS['panel_bg'], width=200, corner_radius=10)
        
        # Title
        title = ctk.CTkLabel(
            panel,
            text="Robot Navigation\nAI Simulator",
            font=("Arial", 14, "bold"),
            text_color=COLORS['accent']
        )
        title.pack(pady=(20, 30), padx=10)
        
        # Difficulty
        difficulty_label = ctk.CTkLabel(
            panel,
            text="Difficulty:",
            font=("Arial", 11, "bold"),
            text_color=COLORS['text_primary']
        )
        difficulty_label.pack(pady=(20, 5), padx=10, anchor="w")
        
        self.difficulty_var = ctk.StringVar(value="Medium")
        difficulty_menu = ctk.CTkOptionMenu(
            panel,
            variable=self.difficulty_var,
            values=["Easy", "Medium", "Hard"],
            fg_color=COLORS['grid_bg'],
            button_color=COLORS['accent'],
            text_color=COLORS['text_primary'],
            dropdown_fg_color=COLORS['panel_bg'],
            dropdown_text_color=COLORS['text_primary']
        )
        difficulty_menu.pack(pady=(0, 15), padx=10, fill=tk.X)
        
        # Speed
        speed_label = ctk.CTkLabel(
            panel,
            text="Simulation Speed:",
            font=("Arial", 11, "bold"),
            text_color=COLORS['text_primary']
        )
        speed_label.pack(pady=(10, 5), padx=10, anchor="w")
        
        self.speed_var = ctk.StringVar(value="Normal")
        speed_menu = ctk.CTkOptionMenu(
            panel,
            variable=self.speed_var,
            values=["Slow", "Normal", "Fast"],
            fg_color=COLORS['grid_bg'],
            button_color=COLORS['accent'],
            text_color=COLORS['text_primary'],
            dropdown_fg_color=COLORS['panel_bg'],
            dropdown_text_color=COLORS['text_primary']
        )
        speed_menu.pack(pady=(0, 20), padx=10, fill=tk.X)
        
        # Buttons
        button_frame = ctk.CTkFrame(panel, fg_color="transparent")
        button_frame.pack(pady=20, padx=10, fill=tk.X)
        
        start_btn = ctk.CTkButton(
            button_frame,
            text="Start Simulation",
            command=self.start_simulation,
            fg_color=COLORS['accent'],
            text_color="#000000",
            font=("Arial", 11, "bold"),
            corner_radius=5
        )
        start_btn.pack(pady=5, fill=tk.X)
        
        generate_btn = ctk.CTkButton(
            button_frame,
            text="Generate New Grid",
            command=self.regenerate_grid,
            fg_color=COLORS['grid_bg'],
            text_color=COLORS['text_primary'],
            font=("Arial", 10),
            corner_radius=5,
            border_width=1,
            border_color=COLORS['accent']
        )
        generate_btn.pack(pady=5, fill=tk.X)
        
        reset_btn = ctk.CTkButton(
            button_frame,
            text="Reset Simulation",
            command=self.reset_simulation,
            fg_color=COLORS['grid_bg'],
            text_color=COLORS['text_primary'],
            font=("Arial", 10),
            corner_radius=5,
            border_width=1,
            border_color=COLORS['text_secondary']
        )
        reset_btn.pack(pady=5, fill=tk.X)
        
        return panel
    
    def create_center_panel(self, parent):
        """Create center grid visualization panel"""
        panel = ctk.CTkFrame(parent, fg_color=COLORS['panel_bg'], corner_radius=10)
        
        # Title
        title = ctk.CTkLabel(
            panel,
            text="Grid Visualization",
            font=("Arial", 12, "bold"),
            text_color=COLORS['accent']
        )
        title.pack(pady=(10, 10))
        
        # Canvas for grid
        canvas_frame = ctk.CTkFrame(panel, fg_color=COLORS['grid_bg'], corner_radius=5)
        canvas_frame.pack(padx=10, pady=(0, 10), fill=tk.BOTH, expand=True)
        
        grid_pixel_size = GRID_SIZE * CELL_SIZE
        self.canvas = tk.Canvas(
            canvas_frame,
            width=grid_pixel_size,
            height=grid_pixel_size,
            bg=COLORS['grid_bg'],
            highlightthickness=0
        )
        self.canvas.pack(padx=5, pady=5)
        
        # Cell mapping for quick redraw
        self.cell_rects: Dict[Tuple[int, int], int] = {}
        
        return panel
    
    def create_right_panel(self, parent):
        """Create right telemetry panel"""
        panel = ctk.CTkFrame(parent, fg_color=COLORS['panel_bg'], width=180, corner_radius=10)
        
        # Title
        title = ctk.CTkLabel(
            panel,
            text="Telemetry",
            font=("Arial", 12, "bold"),
            text_color=COLORS['accent']
        )
        title.pack(pady=(15, 20), padx=10)
        
        # Telemetry items
        telemetry_frame = ctk.CTkFrame(panel, fg_color="transparent")
        telemetry_frame.pack(pady=10, padx=10, fill=tk.X)
        
        # Robot Position
        self.label_robot_pos = ctk.CTkLabel(
            telemetry_frame,
            text="Robot Position:\nX: -  Y: -",
            font=("Arial", 9),
            text_color=COLORS['text_primary'],
            justify="left"
        )
        self.label_robot_pos.pack(pady=8, padx=5, anchor="w")
        
        # Steps Taken
        self.label_steps = ctk.CTkLabel(
            telemetry_frame,
            text="Steps Taken: 0",
            font=("Arial", 9),
            text_color=COLORS['text_primary'],
            justify="left"
        )
        self.label_steps.pack(pady=8, padx=5, anchor="w")
        
        # Nodes Explored
        self.label_nodes = ctk.CTkLabel(
            telemetry_frame,
            text="Nodes Explored: 0",
            font=("Arial", 9),
            text_color=COLORS['text_primary'],
            justify="left"
        )
        self.label_nodes.pack(pady=8, padx=5, anchor="w")
        
        # Elapsed Time
        self.label_time = ctk.CTkLabel(
            telemetry_frame,
            text="Elapsed Time: 0.0s",
            font=("Arial", 9),
            text_color=COLORS['text_primary'],
            justify="left"
        )
        self.label_time.pack(pady=8, padx=5, anchor="w")
        
        # Speed
        self.label_speed = ctk.CTkLabel(
            telemetry_frame,
            text="Speed: Normal",
            font=("Arial", 9),
            text_color=COLORS['text_primary'],
            justify="left"
        )
        self.label_speed.pack(pady=8, padx=5, anchor="w")
        
        # Status
        self.label_status = ctk.CTkLabel(
            telemetry_frame,
            text="Status: Ready",
            font=("Arial", 9),
            text_color=COLORS['text_secondary'],
            justify="left"
        )
        self.label_status.pack(pady=8, padx=5, anchor="w")
        
        return panel
    
    def draw_grid(self):
        """Draw the grid with current state"""
        self.canvas.delete("all")
        self.cell_rects.clear()
        
        # Draw grid background with alternating colors
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                x1 = x * CELL_SIZE
                y1 = y * CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE
                
                # Determine cell color
                if (x, y) == self.grid.robot_pos:
                    color = COLORS['robot']
                elif (x, y) == self.grid.goal_pos:
                    color = COLORS['goal']
                elif (x, y) in self.grid.obstacles:
                    color = COLORS['obstacle']
                elif (x, y) in self.pathfinder.explored_nodes:
                    color = COLORS['explored']
                elif self.robot.path and (x, y) in self.robot.path:
                    color = COLORS['path']
                else:
                    # Checkerboard pattern for empty cells
                    if (x + y) % 2 == 0:
                        color = COLORS['grid_cell_1']
                    else:
                        color = COLORS['grid_cell_2']
                
                rect = self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=color,
                    outline=COLORS['grid_bg'],
                    width=1
                )
                self.cell_rects[(x, y)] = rect
    
    def regenerate_grid(self):
        """Generate a new grid"""
        if self.simulation_running:
            return
        
        # Update difficulty
        difficulty_str = self.difficulty_var.get()
        self.difficulty = getattr(Difficulty, difficulty_str.upper())
        
        # Generate new grid
        self.grid.generate(self.difficulty)
        self.robot = Robot(self.grid)
        self.pathfinder = AStarPathfinder(self.grid)
        
        # Redraw
        self.draw_grid()
        self.update_telemetry()
        self.label_status.configure(text="Status: Ready")
    
    def start_simulation(self):
        """Start the pathfinding and animation"""
        if self.simulation_running:
            return
        
        # Update speed setting
        speed_str = self.speed_var.get()
        self.speed = getattr(Speed, speed_str.upper())
        self.label_speed.configure(text=f"Speed: {speed_str}")
        
        self.simulation_running = True
        self.label_status.configure(text="Status: Finding path...")
        self.root.after(100, self.run_pathfinding)
    
    def run_pathfinding(self):
        """Execute the A* pathfinding algorithm"""
        path, explored = self.pathfinder.find_path()
        self.nodes_explored = len(explored)
        
        if not path:
            self.label_status.configure(text="Status: No path found!")
            self.simulation_running = False
            messagebox.showwarning("No Path", "Goal is unreachable. Regenerating grid...")
            self.regenerate_grid()
            return
        
        self.robot.set_path(path)
        self.draw_grid()
        self.start_time = time.time()
        self.label_status.configure(text="Status: Animating robot...")
        
        self.root.after(500, self.animate_robot)
    
    def animate_robot(self):
        """Animate the robot moving along the path"""
        if not self.simulation_running:
            return
        
        if self.robot.move_along_path():
            self.draw_grid()
            self.update_telemetry()
            delay = self.speed.value
            self.root.after(delay, self.animate_robot)
        else:
            # Robot reached goal
            self.simulation_complete()
    
    def simulation_complete(self):
        """Handle simulation completion"""
        self.simulation_running = False
        elapsed = time.time() - self.start_time
        
        # Draw final state
        self.draw_grid()
        self.update_telemetry()
        
        # Status message
        self.label_status.configure(text="Status: GOAL REACHED")
        
        # Statistics
        stats = (
            f"SIMULATION TERMINATED: GOAL REACHED\n\n"
            f"Total Steps: {self.robot.total_steps}\n"
            f"Elapsed Time: {elapsed:.2f}s\n"
            f"Path Length: {len(self.robot.path)}\n"
            f"Nodes Explored: {self.nodes_explored}"
        )
        
        messagebox.showinfo("Simulation Complete", stats)
    
    def reset_simulation(self):
        """Reset the simulation state"""
        if self.simulation_running:
            return
        
        self.robot.reset()
        self.pathfinder = AStarPathfinder(self.grid)
        self.draw_grid()
        self.update_telemetry()
        self.label_status.configure(text="Status: Ready")
    
    def update_telemetry(self):
        """Update the telemetry display"""
        # Robot position
        self.label_robot_pos.configure(
            text=f"Robot Position:\nX: {self.robot.pos[0]}  Y: {self.robot.pos[1]}"
        )
        
        # Steps
        self.label_steps.configure(text=f"Steps Taken: {self.robot.total_steps}")
        
        # Nodes explored
        self.label_nodes.configure(text=f"Nodes Explored: {self.nodes_explored}")
        
        # Elapsed time
        if self.simulation_running:
            elapsed = time.time() - self.start_time
            self.label_time.configure(text=f"Elapsed Time: {elapsed:.1f}s")


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Initialize and run the application"""
    root = ctk.CTk()
    root.configure(fg_color=COLORS['bg_dark'])
    app = SimulationUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
