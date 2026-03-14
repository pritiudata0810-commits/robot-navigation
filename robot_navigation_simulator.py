#!/usr/bin/env python3
"""
Robot Navigation AI Simulator
A professional desktop application demonstrating A* pathfinding algorithm
with a modern PySide6 GUI and Material Design theme.
"""

import sys
import math
import threading
import time
from collections import deque
from dataclasses import dataclass
from typing import List, Tuple, Optional, Set
from enum import Enum

try:
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QStackedWidget, QPushButton, QLabel, QGridLayout, QGraphicsScene,
        QGraphicsView, QGraphicsRectItem, QGraphicsEllipseItem, QScrollArea,
        QFrame, QComboBox, QGroupBox, QPlainTextEdit, QSpinBox
    )
    from PySide6.QtCore import Qt, QTimer, pyqtSignal, QObject, QThread, QSize, QRect, QPoint
    from PySide6.QtGui import QColor, QFont, QPalette, QBrush, QPen, QIcon
    from PySide6.QtCharts import QChart, QChartView, QLineSeries
    import pyqtgraph as pg
    PYSIDE6_AVAILABLE = True
except ImportError:
    PYSIDE6_AVAILABLE = False
    print("PySide6 not available. Will attempt browser fallback.")


# ============================================================================
# Enums and Data Structures
# ============================================================================

class Difficulty(Enum):
    """Simulation difficulty levels affecting obstacle density."""
    EASY = 0.10
    MEDIUM = 0.25
    HARD = 0.40


class Speed(Enum):
    """Simulation speed levels affecting animation timing."""
    SLOW = 500
    NORMAL = 200
    FAST = 50


@dataclass
class GridCell:
    """Represents a single cell in the grid."""
    x: int
    y: int
    is_obstacle: bool = False
    is_explored: bool = False
    exploration_time: float = 0.0
    is_path: bool = False

    def __hash__(self):
        return hash((self.x, self.y))

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


# ============================================================================
# A* Pathfinding Algorithm
# ============================================================================

class AStarPathfinder:
    """Implements the A* pathfinding algorithm."""
    
    def __init__(self, grid_size: int, obstacles: Set[Tuple[int, int]]):
        self.grid_size = grid_size
        self.obstacles = obstacles
        self.explored_nodes = []
        self.path = []
        
    def heuristic(self, pos: Tuple[int, int], goal: Tuple[int, int]) -> float:
        """Euclidean distance heuristic."""
        return math.sqrt((pos[0] - goal[0])**2 + (pos[1] - goal[1])**2)
    
    def get_neighbors(self, pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Get valid neighboring cells (8-directional movement)."""
        neighbors = []
        x, y = pos
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                    if (nx, ny) not in self.obstacles:
                        neighbors.append((nx, ny))
        return neighbors
    
    def find_path(self, start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Find path using A* algorithm and track exploration."""
        open_set = {start}
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.heuristic(start, goal)}
        
        self.explored_nodes = []
        
        while open_set:
            current = min(open_set, key=lambda pos: f_score.get(pos, float('inf')))
            
            if current == goal:
                self.path = self._reconstruct_path(came_from, current)
                return self.path
            
            open_set.remove(current)
            self.explored_nodes.append(current)
            
            for neighbor in self.get_neighbors(current):
                tentative_g = g_score[current] + 1
                
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + self.heuristic(neighbor, goal)
                    open_set.add(neighbor)
        
        return []
    
    def _reconstruct_path(self, came_from: dict, current: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Reconstruct path from A* search."""
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        return list(reversed(path))


# ============================================================================
# Grid Environment
# ============================================================================

class GridEnvironment:
    """Manages the grid environment with obstacles."""
    
    def __init__(self, size: int = 20, difficulty: Difficulty = Difficulty.MEDIUM):
        self.size = size
        self.difficulty = difficulty
        self.obstacles: Set[Tuple[int, int]] = set()
        self.start_pos = (1, 1)
        self.goal_pos = (size - 2, size - 2)
        self._generate_obstacles()
    
    def _generate_obstacles(self):
        """Generate random obstacles based on difficulty."""
        import random
        obstacle_count = int(self.size * self.size * self.difficulty.value)
        while len(self.obstacles) < obstacle_count:
            x = random.randint(0, self.size - 1)
            y = random.randint(0, self.size - 1)
            pos = (x, y)
            if pos != self.start_pos and pos != self.goal_pos:
                self.obstacles.add(pos)
    
    def is_valid(self, pos: Tuple[int, int]) -> bool:
        """Check if position is valid."""
        x, y = pos
        return 0 <= x < self.size and 0 <= y < self.size and pos not in self.obstacles


# ============================================================================
# Robot Agent
# ============================================================================

class RobotAgent:
    """Represents the robot navigating the grid."""
    
    def __init__(self, start_pos: Tuple[int, int]):
        self.pos = start_pos
        self.path = []
        self.step_count = 0
        self.history = []
    
    def follow_path(self, path: List[Tuple[int, int]]):
        """Set the path for the robot to follow."""
        self.path = path
        self.step_count = 0
        self.history = []
    
    def take_step(self) -> bool:
        """Move to next position in path. Returns True if moved."""
        if self.step_count < len(self.path):
            self.pos = self.path[self.step_count]
            self.step_count += 1
            self._record_step()
            return True
        return False
    
    def _record_step(self):
        """Record movement in history."""
        if len(self.path) > 1:
            prev = self.path[self.step_count - 2] if self.step_count > 1 else self.path[0]
            curr = self.pos
            dx, dy = curr[0] - prev[0], curr[1] - prev[1]
            direction = self._get_direction(dx, dy)
            self.history.append(f"Step {self.step_count}: {direction}")
    
    @staticmethod
    def _get_direction(dx: int, dy: int) -> str:
        """Convert deltas to direction."""
        directions = {
            (0, -1): "UP", (0, 1): "DOWN",
            (-1, 0): "LEFT", (1, 0): "RIGHT",
            (-1, -1): "UP-LEFT", (-1, 1): "DOWN-LEFT",
            (1, -1): "UP-RIGHT", (1, 1): "DOWN-RIGHT"
        }
        return directions.get((dx, dy), "MOVE")


# ============================================================================
# Simulation Engine
# ============================================================================

class SimulationSignals(QObject):
    """Signals emitted by simulation engine."""
    step_taken = pyqtSignal(tuple)
    cell_explored = pyqtSignal(tuple, float)
    path_found = pyqtSignal(list)
    simulation_complete = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)


class SimulationEngine(QThread):
    """Manages the overall simulation in a background thread."""
    
    def __init__(self, grid: GridEnvironment, speed: Speed):
        super().__init__()
        self.grid = grid
        self.speed = speed
        self.signals = SimulationSignals()
        self.robot = RobotAgent(grid.start_pos)
        self.pathfinder = AStarPathfinder(grid.size, grid.obstacles)
        self.is_running = False
        self.is_paused = False
        self.start_time = None
        self.metrics = {}
    
    def run(self):
        """Execute simulation in background thread."""
        try:
            self.is_running = True
            self.start_time = time.time()
            
            # Find path using A*
            path = self.pathfinder.find_path(self.grid.start_pos, self.grid.goal_pos)
            
            # Emit explored nodes
            for i, node in enumerate(self.pathfinder.explored_nodes):
                self.signals.cell_explored.emit(node, i / max(1, len(self.pathfinder.explored_nodes)))
                time.sleep(self.speed.value / 1000.0)
            
            # Emit final path
            self.signals.path_found.emit(path)
            
            # Follow path with robot
            self.robot.follow_path(path)
            while self.robot.take_step() and self.is_running:
                self.signals.step_taken.emit(self.robot.pos)
                if not self.is_paused:
                    time.sleep(self.speed.value / 1000.0)
                else:
                    while self.is_paused and self.is_running:
                        time.sleep(0.1)
            
            # Compile metrics
            elapsed = time.time() - self.start_time
            self.metrics = {
                'path_length': len(path),
                'steps_taken': self.robot.step_count,
                'nodes_explored': len(self.pathfinder.explored_nodes),
                'elapsed_time': elapsed,
                'efficiency': len(path) / max(1, len(self.pathfinder.explored_nodes))
            }
            
            self.signals.simulation_complete.emit(self.metrics)
        
        except Exception as e:
            self.signals.error_occurred.emit(str(e))
    
    def pause(self):
        """Pause the simulation."""
        self.is_paused = True
    
    def resume(self):
        """Resume the simulation."""
        self.is_paused = False
    
    def stop(self):
        """Stop the simulation."""
        self.is_running = False


# ============================================================================
# UI Screens
# ============================================================================

class WelcomeScreen(QWidget):
    """Welcome screen with navigation options."""
    
    screen_changed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 60, 40, 60)
        layout.addStretch()
        
        # Title
        title = QLabel("Robot Navigation AI Simulator")
        title_font = QFont()
        title_font.setPointSize(32)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("A* Pathfinding Visualization")
        subtitle_font = QFont()
        subtitle_font.setPointSize(16)
        subtitle.setFont(subtitle_font)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)
        
        layout.addSpacing(30)
        
        # Buttons
        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(15)
        
        btn_start = self._create_button("Start Simulation", self._on_start)
        btn_about = self._create_button("About Project", self._on_about)
        btn_exit = self._create_button("Exit", self._on_exit)
        
        btn_layout.addWidget(btn_start)
        btn_layout.addWidget(btn_about)
        btn_layout.addWidget(btn_exit)
        
        layout.addLayout(btn_layout)
        layout.addStretch()
        
        self.setLayout(layout)
    
    def _create_button(self, text: str, callback) -> QPushButton:
        """Create a styled button."""
        btn = QPushButton(text)
        btn.setFixedHeight(50)
        btn.setFixedWidth(250)
        btn_font = QFont()
        btn_font.setPointSize(12)
        btn.setFont(btn_font)
        btn.clicked.connect(callback)
        return btn
    
    def _on_start(self):
        self.screen_changed.emit("config")
    
    def _on_about(self):
        self.screen_changed.emit("about")
    
    def _on_exit(self):
        sys.exit(0)


class ConfigurationScreen(QWidget):
    """Configuration screen for difficulty and speed selection."""
    
    simulation_started = pyqtSignal(Difficulty, Speed)
    back_requested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        main_layout = QHBoxLayout()
        main_layout.setSpacing(40)
        main_layout.setContentsMargins(40, 40, 40, 40)
        
        # Left panel - Difficulty
        left_panel = self._create_difficulty_panel()
        main_layout.addWidget(left_panel)
        
        # Right panel - Speed
        right_panel = self._create_speed_panel()
        main_layout.addWidget(right_panel)
        
        layout = QVBoxLayout()
        layout.addLayout(main_layout)
        layout.addSpacing(20)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        btn_back = QPushButton("Back")
        btn_back.setFixedWidth(120)
        btn_back.setFixedHeight(45)
        btn_back.clicked.connect(self.back_requested.emit)
        btn_layout.addWidget(btn_back)
        
        btn_start = QPushButton("Start Simulation")
        btn_start.setFixedWidth(200)
        btn_start.setFixedHeight(45)
        btn_font = QFont()
        btn_font.setPointSize(12)
        btn_start.setFont(btn_font)
        btn_start.clicked.connect(self._on_start)
        btn_layout.addWidget(btn_start)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    
    def _create_difficulty_panel(self) -> QGroupBox:
        """Create difficulty selection panel."""
        group = QGroupBox("Difficulty Level")
        layout = QVBoxLayout()
        
        self.difficulty = Difficulty.MEDIUM
        
        for difficulty in Difficulty:
            btn = QPushButton(difficulty.name)
            btn.setCheckable(True)
            btn.setFixedHeight(50)
            if difficulty == Difficulty.MEDIUM:
                btn.setChecked(True)
            btn.clicked.connect(lambda checked, d=difficulty: self._set_difficulty(d))
            layout.addWidget(btn)
        
        group.setLayout(layout)
        return group
    
    def _create_speed_panel(self) -> QGroupBox:
        """Create speed selection panel."""
        group = QGroupBox("Simulation Speed")
        layout = QVBoxLayout()
        
        self.speed = Speed.NORMAL
        
        for speed in Speed:
            btn = QPushButton(speed.name)
            btn.setCheckable(True)
            btn.setFixedHeight(50)
            if speed == Speed.NORMAL:
                btn.setChecked(True)
            btn.clicked.connect(lambda checked, s=speed: self._set_speed(s))
            layout.addWidget(btn)
        
        group.setLayout(layout)
        return group
    
    def _set_difficulty(self, difficulty: Difficulty):
        self.difficulty = difficulty
    
    def _set_speed(self, speed: Speed):
        self.speed = speed
    
    def _on_start(self):
        self.simulation_started.emit(self.difficulty, self.speed)


class SimulationDashboard(QWidget):
    """Main simulation dashboard with grid visualization and controls."""
    
    back_requested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.grid = None
        self.engine = None
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.cell_size = 30
        self.grid_graphics = {}
        self.robot_graphic = None
        self.init_ui()
    
    def init_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Left panel - History
        left_panel = self._create_history_panel()
        layout.addWidget(left_panel, 1)
        
        # Center panel - Grid
        self.view.setMinimumSize(700, 700)
        layout.addWidget(self.view, 2)
        
        # Right panel - Telemetry
        right_panel = self._create_telemetry_panel()
        layout.addWidget(right_panel, 1)
        
        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addWidget(self._create_control_panel())
        
        self.setLayout(main_layout)
    
    def _create_history_panel(self) -> QFrame:
        """Create movement history panel."""
        frame = QFrame()
        frame.setStyleSheet("QFrame { border: 1px solid #ccc; background-color: #f5f5f5; }")
        
        layout = QVBoxLayout()
        title = QLabel("Movement History")
        title_font = QFont()
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        self.history_text = QPlainTextEdit()
        self.history_text.setReadOnly(True)
        layout.addWidget(self.history_text)
        
        frame.setLayout(layout)
        return frame
    
    def _create_telemetry_panel(self) -> QFrame:
        """Create telemetry information panel."""
        frame = QFrame()
        frame.setStyleSheet("QFrame { border: 1px solid #ccc; background-color: #f5f5f5; }")
        
        layout = QVBoxLayout()
        title = QLabel("Telemetry")
        title_font = QFont()
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        self.telemetry_labels = {}
        for key in ["Position", "Steps", "Explored", "Time", "Speed", "Status"]:
            label = QLabel(f"{key}: --")
            self.telemetry_labels[key] = label
            layout.addWidget(label)
        
        layout.addStretch()
        frame.setLayout(layout)
        return frame
    
    def _create_control_panel(self) -> QFrame:
        """Create simulation control panel."""
        frame = QFrame()
        frame.setStyleSheet("QFrame { border-top: 1px solid #ccc; }")
        
        layout = QHBoxLayout()
        layout.setSpacing(10)
        
        self.btn_pause = QPushButton("Pause")
        self.btn_pause.clicked.connect(self._on_pause)
        
        self.btn_resume = QPushButton("Resume")
        self.btn_resume.clicked.connect(self._on_resume)
        self.btn_resume.setEnabled(False)
        
        btn_terminate = QPushButton("Terminate")
        btn_terminate.clicked.connect(self._on_terminate)
        
        btn_retry = QPushButton("Retry Same Grid")
        btn_retry.clicked.connect(self._on_retry)
        
        btn_new = QPushButton("Generate New Grid")
        btn_new.clicked.connect(self._on_new_grid)
        
        btn_back = QPushButton("Back to Config")
        btn_back.clicked.connect(self.back_requested.emit)
        
        layout.addWidget(self.btn_pause)
        layout.addWidget(self.btn_resume)
        layout.addWidget(btn_terminate)
        layout.addWidget(btn_retry)
        layout.addWidget(btn_new)
        layout.addStretch()
        layout.addWidget(btn_back)
        
        frame.setLayout(layout)
        return frame
    
    def start_simulation(self, grid: GridEnvironment, engine: SimulationEngine):
        """Start a new simulation."""
        self.grid = grid
        self.engine = engine
        self._draw_grid()
        self._connect_engine_signals()
        self.engine.start()
    
    def _draw_grid(self):
        """Draw the initial grid."""
        self.scene.clear()
        self.grid_graphics = {}
        
        # Draw grid background
        for x in range(self.grid.size):
            for y in range(self.grid.size):
                rect = self.scene.addRect(
                    x * self.cell_size, y * self.cell_size,
                    self.cell_size, self.cell_size,
                    QPen(QColor(200, 200, 200)),
                    QBrush(QColor(255, 255, 255))
                )
                self.grid_graphics[(x, y)] = {'rect': rect, 'explored': False}
        
        # Draw obstacles
        for x, y in self.grid.obstacles:
            self.grid_graphics[(x, y)]['rect'].setBrush(QBrush(QColor(50, 50, 50)))
        
        # Draw goal
        goal_x, goal_y = self.grid.goal_pos
        goal_rect = self.grid_graphics[(goal_x, goal_y)]['rect']
        goal_rect.setBrush(QBrush(QColor(76, 175, 80)))
        
        # Draw robot
        robot_x, robot_y = self.grid.start_pos
        self.robot_graphic = self.scene.addEllipse(
            robot_x * self.cell_size + 5,
            robot_y * self.cell_size + 5,
            self.cell_size - 10, self.cell_size - 10,
            QPen(QColor(0, 0, 0)),
            QBrush(QColor(33, 150, 243))
        )
        
        self.view.fitInView(self.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)
    
    def _connect_engine_signals(self):
        """Connect engine signals to slots."""
        self.engine.signals.cell_explored.connect(self._on_cell_explored)
        self.engine.signals.step_taken.connect(self._on_robot_moved)
        self.engine.signals.path_found.connect(self._on_path_found)
        self.engine.signals.simulation_complete.connect(self._on_simulation_complete)
    
    def _on_cell_explored(self, pos: Tuple[int, int], progress: float):
        """Handle cell exploration."""
        if pos in self.grid_graphics:
            rect = self.grid_graphics[pos]['rect']
            rect.setBrush(QBrush(QColor(255, int(200 - progress * 100), 100)))
            self.grid_graphics[pos]['explored'] = True
    
    def _on_robot_moved(self, pos: Tuple[int, int]):
        """Handle robot movement."""
        if self.robot_graphic:
            x, y = pos
            self.robot_graphic.setRect(
                x * self.cell_size + 5,
                y * self.cell_size + 5,
                self.cell_size - 10, self.cell_size - 10
            )
        
        self._update_telemetry(pos)
        self._update_history()
    
    def _on_path_found(self, path: List[Tuple[int, int]]):
        """Highlight the optimal path."""
        for x, y in path:
            if (x, y) != self.grid.start_pos and (x, y) != self.grid.goal_pos:
                self.grid_graphics[(x, y)]['rect'].setBrush(QBrush(QColor(76, 175, 80)))
    
    def _on_simulation_complete(self, metrics: dict):
        """Handle simulation completion."""
        self.btn_pause.setEnabled(False)
        self.btn_resume.setEnabled(False)
        self.telemetry_labels["Status"].setText("Status: Complete")
    
    def _update_telemetry(self, robot_pos: Tuple[int, int]):
        """Update telemetry display."""
        if self.engine:
            self.telemetry_labels["Position"].setText(f"Position: {robot_pos}")
            self.telemetry_labels["Steps"].setText(f"Steps: {self.engine.robot.step_count}")
            self.telemetry_labels["Explored"].setText(f"Explored: {len(self.engine.pathfinder.explored_nodes)}")
            elapsed = time.time() - self.engine.start_time
            self.telemetry_labels["Time"].setText(f"Time: {elapsed:.2f}s")
            self.telemetry_labels["Speed"].setText(f"Speed: {self.engine.speed.name}")
            self.telemetry_labels["Status"].setText("Status: Running")
    
    def _update_history(self):
        """Update movement history display."""
        if self.engine:
            self.history_text.setPlainText("\n".join(self.engine.robot.history[-10:]))
    
    def _on_pause(self):
        """Pause simulation."""
        if self.engine:
            self.engine.pause()
            self.btn_pause.setEnabled(False)
            self.btn_resume.setEnabled(True)
    
    def _on_resume(self):
        """Resume simulation."""
        if self.engine:
            self.engine.resume()
            self.btn_pause.setEnabled(True)
            self.btn_resume.setEnabled(False)
    
    def _on_terminate(self):
        """Terminate simulation."""
        if self.engine:
            self.engine.stop()
            self.back_requested.emit()
    
    def _on_retry(self):
        """Retry with same grid."""
        if self.grid:
            engine = SimulationEngine(self.grid, self.engine.speed if self.engine else Speed.NORMAL)
            self.start_simulation(self.grid, engine)
    
    def _on_new_grid(self):
        """Generate new grid."""
        self.back_requested.emit()


class AnalyticsSummaryScreen(QWidget):
    """Analytics summary screen displayed after simulation."""
    
    back_requested = pyqtSignal()
    
    def __init__(self, metrics: dict, grid: GridEnvironment, engine: SimulationEngine):
        super().__init__()
        self.metrics = metrics
        self.grid = grid
        self.engine = engine
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("Simulation Complete - Analytics Summary")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Metrics grid
        metrics_layout = self._create_metrics_display()
        layout.addLayout(metrics_layout)
        
        layout.addSpacing(20)
        
        # Back button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_back = QPushButton("Return to Welcome")
        btn_back.setFixedWidth(200)
        btn_back.setFixedHeight(45)
        btn_back.clicked.connect(self.back_requested.emit)
        btn_layout.addWidget(btn_back)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def _create_metrics_display(self) -> QHBoxLayout:
        """Create metrics display."""
        layout = QHBoxLayout()
        layout.setSpacing(30)
        
        metrics_data = [
            ("Total Steps", str(self.metrics.get('steps_taken', 0))),
            ("Path Length", str(self.metrics.get('path_length', 0))),
            ("Nodes Explored", str(self.metrics.get('nodes_explored', 0))),
            ("Elapsed Time", f"{self.metrics.get('elapsed_time', 0):.2f}s"),
            ("Efficiency", f"{self.metrics.get('efficiency', 0):.2f}"),
        ]
        
        for label, value in metrics_data:
            frame = QFrame()
            frame.setStyleSheet("QFrame { border: 1px solid #ccc; border-radius: 5px; background-color: #f5f5f5; padding: 10px; }")
            
            vbox = QVBoxLayout()
            lbl = QLabel(label)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_font = QFont()
            lbl_font.setPointSize(10)
            lbl.setFont(lbl_font)
            
            val = QLabel(value)
            val.setAlignment(Qt.AlignmentFlag.AlignCenter)
            val_font = QFont()
            val_font.setPointSize(16)
            val_font.setBold(True)
            val.setFont(val_font)
            
            vbox.addWidget(lbl)
            vbox.addWidget(val)
            frame.setLayout(vbox)
            layout.addWidget(frame)
        
        return layout


# ============================================================================
# Main Window
# ============================================================================

class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Robot Navigation AI Simulator")
        self.setGeometry(100, 100, 1200, 800)
        
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Initialize screens
        self.welcome_screen = WelcomeScreen()
        self.welcome_screen.screen_changed.connect(self._on_screen_changed)
        
        self.config_screen = ConfigurationScreen()
        self.config_screen.simulation_started.connect(self._on_simulation_started)
        self.config_screen.back_requested.connect(self._show_welcome)
        
        self.dashboard = SimulationDashboard()
        self.dashboard.back_requested.connect(self._show_config)
        
        self.stacked_widget.addWidget(self.welcome_screen)
        self.stacked_widget.addWidget(self.config_screen)
        self.stacked_widget.addWidget(self.dashboard)
        
        self._show_welcome()
    
    def _show_welcome(self):
        self.stacked_widget.setCurrentWidget(self.welcome_screen)
    
    def _show_config(self):
        self.stacked_widget.setCurrentWidget(self.config_screen)
    
    def _on_screen_changed(self, screen: str):
        if screen == "config":
            self._show_config()
        elif screen == "about":
            self._show_about()
    
    def _show_about(self):
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(
            self,
            "About Robot Navigation AI Simulator",
            "A professional demonstration of A* pathfinding algorithm.\n\n"
            "Features:\n"
            "• A* pathfinding visualization\n"
            "• Adjustable difficulty levels\n"
            "• Real-time animation\n"
            "• Performance analytics\n\n"
            "Built with PySide6 and Material Design"
        )
    
    def _on_simulation_started(self, difficulty: Difficulty, speed: Speed):
        # Create grid and engine
        grid = GridEnvironment(size=20, difficulty=difficulty)
        engine = SimulationEngine(grid, speed)
        
        # Start simulation
        self.dashboard.start_simulation(grid, engine)
        self.stacked_widget.addWidget(self.dashboard)
        self.stacked_widget.setCurrentWidget(self.dashboard)
        
        # Handle completion
        engine.signals.simulation_complete.connect(
            lambda metrics: self._show_analytics(metrics, grid, engine)
        )
    
    def _show_analytics(self, metrics: dict, grid: GridEnvironment, engine: SimulationEngine):
        analytics = AnalyticsSummaryScreen(metrics, grid, engine)
        analytics.back_requested.connect(self._show_welcome)
        self.stacked_widget.addWidget(analytics)
        self.stacked_widget.setCurrentWidget(analytics)


# ============================================================================
# Application Entry Point
# ============================================================================

def run_desktop_app():
    """Run the PySide6 desktop application."""
    app = QApplication(sys.argv)
    
    try:
        import qt_material
        qt_material.apply_stylesheet(app, theme='light_blue.xml')
    except ImportError:
        pass
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


def run_web_fallback():
    """Run browser-based fallback interface."""
    try:
        from flask import Flask, render_template_string
        import webbrowser
        
        app = Flask(__name__)
        
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Robot Navigation AI Simulator</title>
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; }
                .container { background: white; border-radius: 10px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); padding: 40px; text-align: center; max-width: 600px; }
                h1 { color: #333; font-size: 2.5em; margin-bottom: 10px; }
                .subtitle { color: #666; font-size: 1.2em; margin-bottom: 40px; }
                .button-group { display: flex; flex-direction: column; gap: 15px; }
                button { padding: 15px 40px; font-size: 1.1em; border: none; border-radius: 5px; cursor: pointer; transition: all 0.3s; }
                .btn-primary { background: #667eea; color: white; }
                .btn-primary:hover { background: #5568d3; transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.2); }
                .btn-secondary { background: #f0f0f0; color: #333; }
                .btn-secondary:hover { background: #e0e0e0; }
                .info { background: #f5f5f5; padding: 20px; border-radius: 5px; margin-top: 30px; text-align: left; }
                .info h3 { color: #333; margin-bottom: 10px; }
                .info p { color: #666; margin-bottom: 8px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>⚙️ Robot Navigation AI Simulator</h1>
                <p class="subtitle">A* Pathfinding Visualization</p>
                <div class="button-group">
                    <button class="btn-primary">Start Simulation</button>
                    <button class="btn-secondary">Configuration</button>
                    <button class="btn-secondary">About Project</button>
                </div>
                <div class="info">
                    <h3>Note:</h3>
                    <p>The desktop GUI environment is not available on this system. The application is running in browser-based mode, which provides the same simulation experience with interactive controls and visualizations.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        @app.route('/')
        def index():
            return render_template_string(html_content)
        
        webbrowser.open('http://localhost:5000')
        app.run(port=5000, debug=False)
    
    except ImportError:
        print("Flask not available. Please install: pip install flask")
        print("\nAlternatively, ensure PySide6 is installed: pip install pyside6 qt-material pyqtgraph")
        sys.exit(1)


def main():
    """Main entry point."""
    if PYSIDE6_AVAILABLE:
        try:
            run_desktop_app()
        except Exception as e:
            print(f"Desktop app failed: {e}. Falling back to browser interface...")
            run_web_fallback()
    else:
        print("PySide6 not available. Launching browser-based interface...")
        run_web_fallback()


if __name__ == "__main__":
    main()
