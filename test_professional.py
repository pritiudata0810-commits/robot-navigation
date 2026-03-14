#!/usr/bin/env python3
"""
Automated test for professional navigator
Runs without user interaction
"""

import sys
import os

# Set up path
sys.path.insert(0, 'D:\\robot-navigation')
os.chdir('D:\\robot-navigation')

def test_professional_navigator():
    """Test the professional navigator"""
    
    print("\n" + "=" * 70)
    print("PROFESSIONAL NAVIGATOR - AUTOMATED TEST")
    print("=" * 70)
    
    try:
        # Import
        print("\n[1/5] Importing module...")
        from navigator_professional import (
            Difficulty, Speed, GridConfig, NavigationGrid,
            SimulationState, Point, DashboardRenderer,
            RobotNavigationSimulator
        )
        print("      ✓ All imports successful")
        
        # Create grid
        print("\n[2/5] Testing grid generation...")
        
        for difficulty in [Difficulty.SLOW, Difficulty.MEDIUM, Difficulty.HARD]:
            config = GridConfig(size=10, difficulty=difficulty)
            grid = NavigationGrid(config)
            wall_count = sum(sum(row) for row in grid.grid)
            expected = config.get_wall_count()
            print(f"      ✓ {difficulty.name}: {wall_count} walls (expected ~{expected})")
            
            # Verify start and goal
            assert grid.start == Point(0, 0), "Start position incorrect"
            assert grid.goal == Point(9, 9), "Goal position incorrect"
            assert not grid.is_wall(0, 0), "Start is blocked"
            assert not grid.is_wall(9, 9), "Goal is blocked"
        
        # Test A* pathfinding
        print("\n[3/5] Testing A* pathfinding...")
        config = GridConfig(size=10, difficulty=Difficulty.MEDIUM)
        grid = NavigationGrid(config)
        
        path = grid.calculate_path_astar()
        assert len(path) > 0, "No path found"
        assert path[0] == grid.start, "Path doesn't start at start position"
        assert path[-1] == grid.goal, "Path doesn't end at goal position"
        
        # Verify path is valid (consecutive steps are neighbors)
        for i in range(len(path) - 1):
            p1 = path[i]
            p2 = path[i + 1]
            distance = abs(p1.x - p2.x) + abs(p1.y - p2.y)
            assert distance == 1, f"Path has invalid jump from {p1} to {p2}"
        
        print(f"      ✓ A* found valid path: {len(path)} nodes")
        
        # Test simulation state
        print("\n[4/5] Testing simulation state...")
        state = SimulationState()
        assert state.current_step == 0, "Initial step should be 0"
        assert state.elapsed_time == 0.0, "Initial time should be 0"
        assert len(state.move_log) == 0, "Initial move log should be empty"
        
        state.robot_pos = Point(5, 5)
        state.current_step = 10
        assert state.robot_pos == Point(5, 5), "Position not updated"
        assert state.current_step == 10, "Step not updated"
        print(f"      ✓ Simulation state works correctly")
        
        # Test dashboard renderer
        print("\n[5/5] Testing dashboard renderer...")
        renderer = DashboardRenderer()
        
        # Create test data
        config = GridConfig(size=8, difficulty=Difficulty.SLOW)
        grid = NavigationGrid(config)
        state = SimulationState()
        state.robot_pos = Point(2, 2)
        state.total_steps = 15
        state.move_log = ["Move #1: right", "Move #2: down"]
        
        # Render panels (without displaying)
        try:
            left_panel = renderer.render_live_logs(state, max_visible=5)
            center_panel = renderer.render_navigation_grid(grid, state)
            right_panel = renderer.render_telemetry(state, Speed.NORMAL)
            print(f"      ✓ Dashboard rendering works")
        except Exception as e:
            print(f"      ✗ Dashboard rendering failed: {e}")
            raise
        
        # Test menu system
        print("\n[BONUS] Testing menu system components...")
        from navigator_professional import MenuSystem
        print(f"      ✓ MenuSystem imported")
        
        print("\n" + "=" * 70)
        print("✅ ALL TESTS PASSED")
        print("=" * 70)
        print("\nThe professional navigator is ready to use!")
        print("Run: python navigator_professional.py")
        
        return True
        
    except AssertionError as e:
        print(f"\n      ✗ Assertion failed: {e}")
        return False
    except Exception as e:
        print(f"\n      ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_professional_navigator()
    sys.exit(0 if success else 1)
