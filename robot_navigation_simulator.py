#!/usr/bin/env python3
"""
Robot Navigation AI Simulator - Professional Desktop Application
A visually impressive desktop application demonstrating A* pathfinding algorithm
with modern PySide6 GUI, Material Design theme, smooth animations, and real-time analytics.

Installation: pip install pyside6 qt-material pyqtgraph
Usage: python robot_navigation_simulator.py
"""

import sys
import os
import math
import time
import random
import heapq
import threading
import json
from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple, Optional, Set
from collections import deque

try:
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QStackedWidget, QPushButton, QLabel, QGridLayout, QGraphicsScene,
        QGraphicsView, QGraphicsItem, QGraphicsRectItem, QGraphicsEllipseItem,
        QGraphicsPathItem, QGraphicsPolygonItem, QScrollArea, QFrame,
        QTextEdit, QRadioButton, QButtonGroup, QProgressBar, QMessageBox
    )
    from PySide6.QtCore import (
        Qt, QTimer, pyqtSignal, QObject, QThread, QSize, QRect, QPoint,
        QPointF, QLine, QLineF
    )
    from PySide6.QtGui import (
        QColor, QFont, QPalette, QBrush, QPen, QIcon, QPainter,
        QPolygonF, QLinearGradient, QRadialGradient
    )

    try:
        import qt_material
        QT_MATERIAL_AVAILABLE = True
    except ImportError:
        QT_MATERIAL_AVAILABLE = False

    try:
        import pyqtgraph as pg
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        PYQTGRAPH_AVAILABLE = True
    except ImportError:
        PYQTGRAPH_AVAILABLE = False

    PYSIDE6_AVAILABLE = True

except ImportError as e:
    PYSIDE6_AVAILABLE = False
    print(f"Warning: PySide6 not available ({e}). Consider installing: pip install pyside6 qt-material pyqtgraph")


# ============================================================================
# Core Enums and Data Structures
# ============================================================================

class Difficulty(Enum):
    """Simulation difficulty levels affecting obstacle density"""
    EASY = 0.15
    MEDIUM = 0.30
    HARD = 0.50


class SimulationSpeed(Enum):
    """Speed settings for animation timing (milliseconds per step)"""
    SLOW = 500
    NORMAL = 200
    FAST = 50


@dataclass
class Point:
    """2D point representation"""
    x: int
    y: int

    def __hash__(self):
        return hash((self.x, self.y))

    def __eq__(self, other):
        if not isinstance(other, Point):
            return False
        return self.x == other.x and self.y == other.y

    def distance_to(self, other: 'Point') -> float:
        """Euclidean distance to another point"""
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    def manhattan_distance(self, other: 'Point') -> int:
        """Manhattan distance to another point"""
        return abs(self.x - other.x) + abs(self.y - other.y)


# ============================================================================
# A* Pathfinding Algorithm
# ============================================================================

class AStarPathfinder:
    """Implements the A* pathfinding algorithm with real-time node tracking"""

    def __init__(self, grid_size: int = 20):
        self.grid_size = grid_size
        self.obstacles: Set[Point] = set()
        self.explored_nodes: List[Point] = []
        self.path: List[Point] = []

    def set_obstacles(self, obstacles: Set[Point]):
        """Set obstacle positions in the grid"""
        self.obstacles = obstacles

    def heuristic(self, pos: Point, goal: Point) -> float:
        """Manhattan distance heuristic for A*"""
        return float(pos.manhattan_distance(goal))

    def get_neighbors(self, pos: Point) -> List[Point]:
        """Get valid neighboring cells (4-directional movement only)"""
        neighbors = []
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        for dx, dy in directions:
            new_x, new_y = pos.x + dx, pos.y + dy
            if 0 <= new_x < self.grid_size and 0 <= new_y < self.grid_size:
                new_pos = Point(new_x, new_y)
                if new_pos not in self.obstacles:
                    neighbors.append(new_pos)
        return neighbors

    def find_path(self, start: Point, goal: Point) -> List[Point]:
        """Execute A* pathfinding algorithm"""
        self.explored_nodes = []
        self.path = []

        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.heuristic(start, goal)}
        closed_set = set()

        while open_set:
            _, current = heapq.heappop(open_set)

            if current in closed_set:
                continue

            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                self.path = list(reversed(path))
                return self.path

            closed_set.add(current)
            self.explored_nodes.append(current)

            for neighbor in self.get_neighbors(current):
                if neighbor in closed_set:
                    continue

                tentative_g = g_score[current] + 1
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + self.heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

        return []


# ============================================================================
# Grid Environment
# ============================================================================

class GridEnvironment:
    """Manages the grid environment with obstacles"""

    def __init__(self, size: int = 20, obstacle_density: float = 0.2):
        self.size = size
        self.obstacle_density = obstacle_density
        self.obstacles: Set[Point] = set()
        self.start = Point(1, 1)
        self.goal = Point(size - 2, size - 2)
        self.generate_obstacles()

    def generate_obstacles(self):
        """Generate random obstacles based on density"""
        self.obstacles.clear()
        for x in range(self.size):
            for y in range(self.size):
                if (Point(x, y) == self.start) or (Point(x, y) == self.goal):
                    continue
                if random.random() < self.obstacle_density:
                    self.obstacles.add(Point(x, y))

    def is_obstacle(self, point: Point) -> bool:
        """Check if point is an obstacle"""
        return point in self.obstacles


# ============================================================================
# Robot Agent
# ============================================================================

class RobotAgent:
    """Represents the robot navigating the grid"""

    def __init__(self, start_pos: Point):
        self.position = start_pos
        self.path: List[Point] = []
        self.path_index = 0
        self.step_count = 0
        self.movement_history = []

    def set_path(self, path: List[Point]):
        """Set the path to follow"""
        self.path = path
        self.path_index = 0
        self.step_count = 0
        self.movement_history = []

    def move_to_next(self) -> bool:
        """Move to next position on path. Returns True if moved."""
        if self.path_index < len(self.path) - 1:
            self.path_index += 1
            prev_pos = self.path[self.path_index - 1]
            self.position = self.path[self.path_index]
            self.step_count += 1

            dx = self.position.x - prev_pos.x
            dy = self.position.y - prev_pos.y

            if dx > 0:
                direction = "RIGHT"
            elif dx < 0:
                direction = "LEFT"
            elif dy > 0:
                direction = "DOWN"
            else:
                direction = "UP"

            self.movement_history.append(f"Step {self.step_count} → {direction}")
            return True
        return False

    def is_at_goal(self) -> bool:
        """Check if robot reached the goal"""
        return self.path_index == len(self.path) - 1


# ============================================================================
# Simulation Signals and Engine
# ============================================================================

class SimulationSignals(QObject):
    """Signals emitted by simulation engine"""
    robot_moved = pyqtSignal(int, int)
    explored_updated = pyqtSignal(list)
    simulation_finished = pyqtSignal(dict)
    status_changed = pyqtSignal(str)
    time_updated = pyqtSignal(float)


class SimulationEngine(QThread):
    """Manages simulation execution in a separate thread"""

    def __init__(self, grid: GridEnvironment, difficulty: Difficulty, speed: SimulationSpeed):
        super().__init__()
        self.grid = grid
        self.difficulty = difficulty
        self.speed = speed
        self.signals = SimulationSignals()
        self.running = False
        self.paused = False
        self.robot = RobotAgent(grid.start)
        self.pathfinder = AStarPathfinder(grid.size)
        self.pathfinder.set_obstacles(grid.obstacles)
        self.start_time = 0
        self.elapsed_time = 0

    def run(self):
        """Run the simulation"""
        self.running = True
        self.start_time = time.time()

        self.signals.status_changed.emit("Finding optimal path...")
        self.pathfinder.find_path(self.grid.start, self.grid.goal)

        if not self.pathfinder.path:
            self.signals.status_changed.emit("No path found!")
            self.running = False
            return

        self.robot.set_path(self.pathfinder.path)

        self.signals.status_changed.emit("Simulating robot movement...")

        while self.running and self.robot.move_to_next():
            if not self.paused:
                self.elapsed_time = time.time() - self.start_time
                self.signals.robot_moved.emit(self.robot.position.x, self.robot.position.y)
                self.signals.explored_updated.emit(self.pathfinder.explored_nodes)
                self.signals.time_updated.emit(self.elapsed_time)
                self.msleep(int(self.speed.value))

        if self.running:
            self.signals.status_changed.emit("Simulation complete!")
            self.emit_final_results()

    def emit_final_results(self):
        """Emit final simulation results"""
        results = {
            'total_steps': self.robot.step_count,
            'path_length': len(self.pathfinder.path),
            'nodes_explored': len(self.pathfinder.explored_nodes),
            'elapsed_time': self.elapsed_time,
            'efficiency': (len(self.pathfinder.path) / max(len(self.pathfinder.explored_nodes), 1)) * 100
        }
        self.signals.simulation_finished.emit(results)

    def pause_simulation(self):
        """Pause the simulation"""
        self.paused = True

    def resume_simulation(self):
        """Resume the simulation"""
        self.paused = False

    def stop_simulation(self):
        """Stop the simulation"""
        self.running = False


# ============================================================================
# Grid Canvas Visualization
# ============================================================================

class GridCanvasWidget(QGraphicsView):
    """Custom graphics view for rendering the grid and simulation"""

    def __init__(self, grid: GridEnvironment):
        super().__init__()
        self.grid = grid
        self.cell_size = 30
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setStyleSheet("background-color: #ffffff; border: 2px solid #ccc;")
        self.setRenderHint(QPainter.Antialiasing)
        self.explored_cells = {}
        self.path_cells = set()
        self.robot_item = None
        self.draw_grid()

    def draw_grid(self):
        """Draw the initial grid with obstacles"""
        self.scene.clear()
        self.explored_cells.clear()
        self.path_cells.clear()

        for x in range(self.grid.size):
            for y in range(self.grid.size):
                rect = self.scene.addRect(
                    x * self.cell_size, y * self.cell_size,
                    self.cell_size, self.cell_size,
                    QPen(QColor("#e0e0e0")), QBrush(QColor("#ffffff"))
                )
                rect.setZValue(0)

        for obstacle in self.grid.obstacles:
            rect = self.scene.addRect(
                obstacle.x * self.cell_size, obstacle.y * self.cell_size,
                self.cell_size, self.cell_size,
                QPen(QColor("#555")), QBrush(QColor("#333333"))
            )
            rect.setZValue(1)

        goal_rect = self.scene.addRect(
            self.grid.goal.x * self.cell_size, self.grid.goal.y * self.cell_size,
            self.cell_size, self.cell_size,
            QPen(QColor("#ff6b6b"), 2), QBrush(QColor("#ffcdd2"))
        )
        goal_rect.setZValue(2)

        self.draw_robot(self.grid.start)
        self.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)

    def draw_robot(self, pos: Point):
        """Draw the robot at position"""
        if self.robot_item:
            self.scene.removeItem(self.robot_item)

        robot_size = self.cell_size - 4
        robot_rect = self.scene.addRect(
            pos.x * self.cell_size + 2, pos.y * self.cell_size + 2,
            robot_size, robot_size,
            QPen(QColor("#2e7d32"), 2), QBrush(QColor("#66BB6A"))
        )
        robot_rect.setZValue(5)
        self.robot_item = robot_rect

    def update_explored_nodes(self, explored: List[Point]):
        """Update visualization of explored nodes with gradient"""
        for i, point in enumerate(explored):
            if point not in self.explored_cells:
                intensity = 100 + int(100 * (i / max(1, len(explored))))
                color = QColor(100, 150, min(255, intensity))
                rect = self.scene.addRect(
                    point.x * self.cell_size + 1, point.y * self.cell_size + 1,
                    self.cell_size - 2, self.cell_size - 2,
                    QPen(color), QBrush(color)
                )
                rect.setZValue(1)
                self.explored_cells[point] = rect

    def highlight_path(self, path: List[Point]):
        """Highlight the optimal path"""
        for point in path:
            if point != self.grid.start and point != self.grid.goal:
                rect = self.scene.addRect(
                    point.x * self.cell_size + 2, point.y * self.cell_size + 2,
                    self.cell_size - 4, self.cell_size - 4,
                    QPen(QColor("#2196F3"), 2), QBrush(QColor("#64B5F6"))
                )
                rect.setZValue(3)
                self.path_cells.add(point)


# ============================================================================
# UI Screens - Welcome
# ============================================================================

class WelcomeScreen(QWidget):
    """Welcome screen with navigation"""

    start_simulation = pyqtSignal()
    show_about = pyqtSignal()
    exit_app = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 60, 40, 60)
        layout.setSpacing(20)

        title = QLabel("Robot Navigation AI Simulator")
        title_font = QFont()
        title_font.setPointSize(48)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("A* Pathfinding Visualization")
        subtitle_font = QFont()
        subtitle_font.setPointSize(24)
        subtitle.setFont(subtitle_font)
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #666; margin-bottom: 40px;")
        layout.addWidget(subtitle)

        layout.addSpacing(40)

        btn_start = self.create_button("Start Simulation", "#4CAF50")
        btn_start.clicked.connect(self.start_simulation.emit)
        layout.addWidget(btn_start)

        btn_about = self.create_button("About Project", "#2196F3")
        btn_about.clicked.connect(self.show_about.emit)
        layout.addWidget(btn_about)

        btn_exit = self.create_button("Exit", "#f44336")
        btn_exit.clicked.connect(self.exit_app.emit)
        layout.addWidget(btn_exit)

        layout.addStretch()
        self.setLayout(layout)

    def create_button(self, text: str, color: str) -> QPushButton:
        """Create a styled button"""
        btn = QPushButton(text)
        btn.setFixedHeight(50)
        btn_font = QFont()
        btn_font.setPointSize(16)
        btn_font.setBold(True)
        btn.setFont(btn_font)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                padding: 10px;
            }}
            QPushButton:hover {{
                background-color: {self.adjust_color(color, 20)};
            }}
            QPushButton:pressed {{
                background-color: {self.adjust_color(color, -20)};
            }}
        """)
        return btn

    @staticmethod
    def adjust_color(color: str, amount: int) -> str:
        """Adjust color brightness"""
        r = int(color[1:3], 16) + amount
        g = int(color[3:5], 16) + amount
        b = int(color[5:7], 16) + amount
        r, g, b = max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b))
        return f"#{r:02x}{g:02x}{b:02x}"


# ============================================================================
# UI Screens - Simulation Dashboard
# ============================================================================

class SimulationDashboard(QWidget):
    """Main simulation dashboard with grid visualization and controls"""

    pause_simulation = pyqtSignal()
    resume_simulation = pyqtSignal()
    terminate_simulation = pyqtSignal()
    retry_simulation = pyqtSignal()
    new_grid_simulation = pyqtSignal()
    back_to_config = pyqtSignal()

    def __init__(self, grid: GridEnvironment):
        super().__init__()
        self.grid = grid
        self.init_ui()

    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        main_content = QHBoxLayout()
        main_content.setSpacing(10)

        main_content.addWidget(self.create_log_panel(), 1)
        main_content.addWidget(self.create_canvas(), 2)
        main_content.addWidget(self.create_telemetry_panel(), 1)

        layout.addLayout(main_content, 1)
        layout.addWidget(self.create_control_panel())

        self.setLayout(layout)

    def create_log_panel(self) -> QWidget:
        """Create movement history log panel"""
        panel = QFrame()
        panel.setStyleSheet("background-color: #fafafa; border: 1px solid #e0e0e0; border-radius: 5px;")
        layout = QVBoxLayout()

        title = QLabel("Movement History")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(11)
        title.setFont(title_font)
        layout.addWidget(title)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: none;
                font-family: Courier;
                font-size: 10pt;
            }
        """)
        layout.addWidget(self.log_text)

        panel.setLayout(layout)
        return panel

    def create_canvas(self) -> QWidget:
        """Create grid canvas"""
        panel = QFrame()
        panel.setStyleSheet("background-color: #fafafa; border: 1px solid #e0e0e0; border-radius: 5px;")
        layout = QVBoxLayout()

        title = QLabel("Grid Simulation")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(11)
        title.setFont(title_font)
        layout.addWidget(title)

        self.canvas = GridCanvasWidget(self.grid)
        layout.addWidget(self.canvas)

        panel.setLayout(layout)
        return panel

    def create_telemetry_panel(self) -> QWidget:
        """Create telemetry information panel"""
        panel = QFrame()
        panel.setStyleSheet("background-color: #fafafa; border: 1px solid #e0e0e0; border-radius: 5px;")
        layout = QVBoxLayout()

        title = QLabel("Telemetry")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(11)
        title.setFont(title_font)
        layout.addWidget(title)

        self.telemetry_items = {}
        for key in ['Robot Position', 'Steps Taken', 'Nodes Explored', 'Elapsed Time', 'Current Status']:
            label = QLabel(key)
            label_font = QFont()
            label_font.setBold(True)
            label_font.setPointSize(9)
            label.setFont(label_font)
            layout.addWidget(label)

            value = QLabel("--")
            value_font = QFont()
            value_font.setPointSize(10)
            value.setFont(value_font)
            value.setStyleSheet("color: #2196F3; margin-left: 10px; margin-bottom: 15px;")
            layout.addWidget(value)

            self.telemetry_items[key] = value

        layout.addStretch()
        panel.setLayout(layout)
        return panel

    def create_control_panel(self) -> QWidget:
        """Create control panel"""
        panel = QFrame()
        panel.setStyleSheet("background-color: #f5f5f5; border-top: 1px solid #e0e0e0; padding: 15px;")
        layout = QHBoxLayout()

        btn_pause = self.create_control_button("Pause", "#FF9800")
        btn_pause.clicked.connect(self.pause_simulation.emit)
        layout.addWidget(btn_pause)

        btn_resume = self.create_control_button("Resume", "#4CAF50")
        btn_resume.clicked.connect(self.resume_simulation.emit)
        layout.addWidget(btn_resume)

        btn_terminate = self.create_control_button("Terminate", "#f44336")
        btn_terminate.clicked.connect(self.terminate_simulation.emit)
        layout.addWidget(btn_terminate)

        btn_retry = self.create_control_button("Retry Same Grid", "#9C27B0")
        btn_retry.clicked.connect(self.retry_simulation.emit)
        layout.addWidget(btn_retry)

        btn_new = self.create_control_button("Generate New Grid", "#2196F3")
        btn_new.clicked.connect(self.new_grid_simulation.emit)
        layout.addWidget(btn_new)

        panel.setLayout(layout)
        panel.setFixedHeight(60)
        return panel

    @staticmethod
    def create_control_button(text: str, color: str) -> QPushButton:
        """Create a control button"""
        btn = QPushButton(text)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 3px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {WelcomeScreen.adjust_color(color, 20)};
            }}
        """)
        return btn

    def update_log(self, step: int, direction: str):
        """Update movement log"""
        log_text = self.log_text.toPlainText()
        log_text += f"Step {step} → {direction}\n"
        self.log_text.setText(log_text)
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )

    def update_telemetry(self, key: str, value: str):
        """Update telemetry display"""
        if key in self.telemetry_items:
            self.telemetry_items[key].setText(value)

    def update_robot_position(self, x: int, y: int):
        """Update robot position display"""
        old_pos = self.telemetry_items['Robot Position'].text()
        try:
            old_x, old_y = map(int, old_pos.split(', '))
            if old_x == x and old_y == y:
                return

            dx = x - old_x
            dy = y - old_y
            if dx > 0:
                direction = "RIGHT"
            elif dx < 0:
                direction = "LEFT"
            elif dy > 0:
                direction = "DOWN"
            else:
                direction = "UP"

            steps = int(self.telemetry_items['Steps Taken'].text()) + 1
        except:
            direction = "START"
            steps = 0

        self.update_telemetry('Robot Position', f"{x}, {y}")
        self.update_telemetry('Steps Taken', str(steps))
        self.update_log(steps, direction)
        self.canvas.draw_robot(Point(x, y))



# ============================================================================
# UI Screens - Analytics Summary
# ============================================================================

class AnalyticsSummaryScreen(QWidget):
    """Analytics summary screen"""

    back_to_config = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.results = {}
        self.init_ui()

    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        title = QLabel("Simulation Complete - Analytics Summary")
        title_font = QFont()
        title_font.setPointSize(28)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(20)

        self.metric_labels = {}
        for metric in ['Total Steps', 'Path Length', 'Nodes Explored', 'Elapsed Time', 'Efficiency %']:
            metric_panel = QFrame()
            metric_panel.setStyleSheet("""
                QFrame {
                    background-color: #f5f5f5;
                    border: 1px solid #e0e0e0;
                    border-radius: 5px;
                    padding: 20px;
                }
            """)
            metric_layout = QVBoxLayout()

            label = QLabel(metric)
            label_font = QFont()
            label_font.setPointSize(12)
            label_font.setBold(True)
            label.setFont(label_font)
            label.setAlignment(Qt.AlignCenter)
            metric_layout.addWidget(label)

            value = QLabel("--")
            value_font = QFont()
            value_font.setPointSize(24)
            value_font.setBold(True)
            value.setFont(value_font)
            value.setAlignment(Qt.AlignCenter)
            value.setStyleSheet("color: #2196F3;")
            metric_layout.addWidget(value)

            self.metric_labels[metric] = value
            metric_panel.setLayout(metric_layout)
            metrics_layout.addWidget(metric_panel)

        layout.addLayout(metrics_layout)

        btn_back = QPushButton("Back to Configuration")
        btn_back.setFixedHeight(45)
        btn_back_font = QFont()
        btn_back_font.setPointSize(12)
        btn_back_font.setBold(True)
        btn_back.setFont(btn_back_font)
        btn_back.setStyleSheet("""
            QPushButton {
                background-color: #757575;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #9e9e9e;
            }
        """)
        btn_back.clicked.connect(self.back_to_config.emit)
        layout.addWidget(btn_back)

        self.setLayout(layout)

    def set_results(self, results: dict):
        """Set and display results"""
        self.results = results
        self.metric_labels['Total Steps'].setText(str(results.get('total_steps', 0)))
        self.metric_labels['Path Length'].setText(str(results.get('path_length', 0)))
        self.metric_labels['Nodes Explored'].setText(str(results.get('nodes_explored', 0)))
        elapsed = results.get('elapsed_time', 0)
        self.metric_labels['Elapsed Time'].setText(f"{elapsed:.2f}s")
        efficiency = results.get('efficiency', 0)
        self.metric_labels['Efficiency %'].setText(f"{efficiency:.1f}%")


# ============================================================================
# Main Application Window
# ============================================================================

class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Robot Navigation AI Simulator")
        self.setGeometry(100, 100, 1400, 900)

        self.current_grid = None
        self.simulation_thread = None
        self.last_difficulty = Difficulty.MEDIUM
        self.last_speed = SimulationSpeed.NORMAL

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.welcome_screen = WelcomeScreen()
        self.config_screen = ConfigurationScreen()
        self.analytics_screen = AnalyticsSummaryScreen()

        self.stacked_widget.addWidget(self.welcome_screen)
        self.stacked_widget.addWidget(self.config_screen)
        self.stacked_widget.addWidget(self.analytics_screen)

        self.setup_connections()
        self.apply_theme()
        self.stacked_widget.setCurrentIndex(0)

    def setup_connections(self):
        """Setup signal connections"""
        self.welcome_screen.start_simulation.connect(self.on_start_simulation)
        self.welcome_screen.exit_app.connect(self.close)
        self.welcome_screen.show_about.connect(self.show_about_dialog)

        self.config_screen.start_simulation_with_config.connect(self.start_simulation)
        self.config_screen.back_to_welcome.connect(
            lambda: self.stacked_widget.setCurrentIndex(0)
        )

        self.analytics_screen.back_to_config.connect(self.on_back_to_config)

    def on_start_simulation(self):
        """Transition to configuration screen"""
        self.stacked_widget.setCurrentIndex(1)

    def start_simulation(self, difficulty: Difficulty, speed: SimulationSpeed):
        """Start the simulation"""
        self.current_grid = GridEnvironment(size=20, obstacle_density=difficulty.value)
        self.simulation_dashboard = SimulationDashboard(self.current_grid)

        self.setup_dashboard_connections()

        self.stacked_widget.insertWidget(2, self.simulation_dashboard)
        self.stacked_widget.setCurrentIndex(2)

        self.start_simulation_engine(speed)

    def setup_dashboard_connections(self):
        """Setup dashboard signal connections"""
        self.simulation_dashboard.pause_simulation.connect(self.pause_simulation)
        self.simulation_dashboard.resume_simulation.connect(self.resume_simulation)
        self.simulation_dashboard.terminate_simulation.connect(self.terminate_simulation)
        self.simulation_dashboard.retry_simulation.connect(
            lambda: self.start_simulation(
                self.last_difficulty, self.last_speed
            )
        )
        self.simulation_dashboard.new_grid_simulation.connect(
            lambda: self.start_simulation(
                self.last_difficulty, self.last_speed
            )
        )

    def start_simulation_engine(self, speed: SimulationSpeed):
        """Start the simulation engine thread"""
        self.last_difficulty = self.config_screen.difficulty
        self.last_speed = speed

        self.simulation_thread = SimulationEngine(self.current_grid, self.last_difficulty, speed)

        self.simulation_thread.signals.robot_moved.connect(self.on_robot_moved)
        self.simulation_thread.signals.explored_updated.connect(self.on_explored_updated)
        self.simulation_thread.signals.simulation_finished.connect(self.on_simulation_finished)
        self.simulation_thread.signals.status_changed.connect(self.on_status_changed)
        self.simulation_thread.signals.time_updated.connect(self.on_time_updated)

        self.simulation_dashboard.update_telemetry('Current Status', 'Initializing...')
        self.simulation_dashboard.update_telemetry('Robot Position', f'{self.current_grid.start.x}, {self.current_grid.start.y}')
        self.simulation_dashboard.update_telemetry('Steps Taken', '0')
        self.simulation_dashboard.update_telemetry('Nodes Explored', '0')
        self.simulation_dashboard.update_telemetry('Elapsed Time', '0.00s')

        self.simulation_thread.start()

    def on_robot_moved(self, x: int, y: int):
        """Handle robot movement"""
        if self.simulation_dashboard:
            self.simulation_dashboard.update_robot_position(x, y)

    def on_explored_updated(self, explored: List[Point]):
        """Handle explored nodes update"""
        if self.simulation_dashboard:
            self.simulation_dashboard.canvas.update_explored_nodes(explored)
            nodes_count = len(explored)
            self.simulation_dashboard.update_telemetry('Nodes Explored', str(nodes_count))

    def on_simulation_finished(self, results: dict):
        """Handle simulation completion"""
        if self.simulation_dashboard:
            self.simulation_dashboard.update_telemetry('Current Status', 'Complete')
            self.simulation_dashboard.canvas.highlight_path(
                self.simulation_thread.pathfinder.path
            )

        self.analytics_screen.set_results(results)
        self.stacked_widget.setCurrentIndex(3)

    def on_status_changed(self, status: str):
        """Handle status change"""
        if self.simulation_dashboard:
            self.simulation_dashboard.update_telemetry('Current Status', status)

    def on_time_updated(self, elapsed: float):
        """Handle time update"""
        if self.simulation_dashboard:
            self.simulation_dashboard.update_telemetry('Elapsed Time', f"{elapsed:.2f}s")

    def pause_simulation(self):
        """Pause the simulation"""
        if self.simulation_thread:
            self.simulation_thread.pause_simulation()

    def resume_simulation(self):
        """Resume the simulation"""
        if self.simulation_thread:
            self.simulation_thread.resume_simulation()

    def terminate_simulation(self):
        """Terminate the simulation"""
        if self.simulation_thread:
            self.simulation_thread.stop_simulation()
            self.simulation_thread.wait()

    def on_back_to_config(self):
        """Handle back to configuration"""
        if self.simulation_thread:
            self.simulation_thread.stop_simulation()
            self.simulation_thread.wait()
        self.stacked_widget.setCurrentIndex(1)

    def show_about_dialog(self):
        """Show about dialog"""
        QMessageBox.information(
            self,
            "About Robot Navigation AI Simulator",
            "Professional AI Robot Navigation Simulator\n\n"
            "Features:\n"
            "• A* Pathfinding Algorithm\n"
            "• Real-time Grid Visualization\n"
            "• Multiple Difficulty Levels\n"
            "• Performance Analytics\n\n"
            "Powered by PySide6 & Material Design"
        )

    def apply_theme(self):
        """Apply modern theme"""
        if QT_MATERIAL_AVAILABLE:
            try:
                qt_material.apply_stylesheet(self, theme='light_blue.xml')
            except:
                pass

        self.setStyleSheet("""
            QMainWindow {
                background-color: #fafafa;
            }
            QLabel {
                color: #333;
            }
        """)

    def closeEvent(self, event):
        """Handle window close"""
        if self.simulation_thread:
            self.simulation_thread.stop_simulation()
            self.simulation_thread.wait()
        event.accept()


# ============================================================================
# Application Entry Point
# ============================================================================

def main():
    """Application entry point"""
    if not PYSIDE6_AVAILABLE:
        print("ERROR: PySide6 is required but not installed.")
        print("Install dependencies with: pip install pyside6 qt-material pyqtgraph")
        sys.exit(1)

    app = QApplication(sys.argv)

    if QT_MATERIAL_AVAILABLE:
        try:
            qt_material.apply_stylesheet(app, theme='light_blue.xml')
        except:
            pass

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
