#!/usr/bin/env python3
"""
Test script for cyberpunk navigator
Verifies all components load and basic rendering works
"""

import sys
import os

# Add repo to path
sys.path.insert(0, 'D:\\robot-navigation')

def test_imports():
    """Test that all required modules import correctly"""
    print("Testing imports...")
    try:
        from navigator import (
            Navigator, Grid, GameState, GameConfig, AStar,
            FogOfWar, Difficulty, Speed, CyberpunkTheme,
            AnimationState, Hazard, AStarMetrics
        )
        print("  ✓ All classes imported successfully")
        return True
    except Exception as e:
        print(f"  ✗ Import failed: {e}")
        return False

def test_theme():
    """Test cyberpunk theme"""
    print("Testing CyberpunkTheme...")
    try:
        from navigator import CyberpunkTheme
        assert CyberpunkTheme.CYAN == "#00FFFF"
        assert CyberpunkTheme.MAGENTA == "#FF00FF"
        assert CyberpunkTheme.NEON_GREEN == "#00FF00"
        color = CyberpunkTheme.depth_color(1)
        assert color == "#0066CC"
        print("  ✓ Theme colors correct")
        return True
    except Exception as e:
        print(f"  ✗ Theme test failed: {e}")
        return False

def test_animation_state():
    """Test animation state"""
    print("Testing AnimationState...")
    try:
        from navigator import AnimationState
        anim = AnimationState()
        assert anim.frame_count == 0
        anim.tick(50)
        assert anim.frame_count == 1
        assert anim.time_ms == 50
        print("  ✓ Animation state working")
        return True
    except Exception as e:
        print(f"  ✗ Animation state test failed: {e}")
        return False

def test_hazard():
    """Test hazard system"""
    print("Testing Hazard system...")
    try:
        from navigator import Hazard
        h = Hazard(5.0, 5.0, 0.2, 0.3)
        assert h.active == True
        initial_x = h.x
        h.update(20)  # Grid size 20
        assert h.x != initial_x or h.y != 5.0
        dist = h.distance_to(5, 5)
        assert dist >= 0
        print("  ✓ Hazard system working")
        return True
    except Exception as e:
        print(f"  ✗ Hazard test failed: {e}")
        return False

def test_grid_creation():
    """Test grid creation"""
    print("Testing Grid creation...")
    try:
        from navigator import Grid, Difficulty
        grid = Grid(size=15, obstacle_percentage=0.10)
        grid.place_obstacles()
        assert grid.start_pos == (0, 0)
        assert grid.goal_pos == (14, 14)
        neighbors = grid.get_neighbors(7, 7)
        assert len(neighbors) > 0
        print("  ✓ Grid creation working")
        return True
    except Exception as e:
        print(f"  ✗ Grid test failed: {e}")
        return False

def test_astar():
    """Test A* pathfinding"""
    print("Testing A* pathfinding...")
    try:
        from navigator import Grid, AStar, Difficulty
        grid = Grid(size=15, obstacle_percentage=0.10)
        grid.place_obstacles()
        astar = AStar(grid)
        path, metrics = astar.find_path()
        assert len(path) > 0
        assert path[0] == (0, 0)
        assert path[-1] == (14, 14)
        assert metrics.nodes_explored > 0
        print(f"  ✓ A* working (path length: {len(path)}, nodes explored: {metrics.nodes_explored})")
        return True
    except Exception as e:
        print(f"  ✗ A* test failed: {e}")
        return False

def test_navigator_creation():
    """Test Navigator initialization"""
    print("Testing Navigator creation...")
    try:
        from navigator import Navigator, GameConfig, Difficulty, Speed
        nav = Navigator()
        assert nav.console is not None
        assert len(nav.particle_trails) == 0
        assert len(nav.hazards) == 0
        print("  ✓ Navigator creation working")
        return True
    except Exception as e:
        print(f"  ✗ Navigator test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("CYBERPUNK NAVIGATOR - COMPONENT TESTS")
    print("="*60 + "\n")
    
    tests = [
        test_imports,
        test_theme,
        test_animation_state,
        test_hazard,
        test_grid_creation,
        test_astar,
        test_navigator_creation,
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"  ✗ Unexpected error: {e}")
            results.append(False)
        print()
    
    # Summary
    passed = sum(results)
    total = len(results)
    print("="*60)
    print(f"RESULTS: {passed}/{total} tests passed")
    print("="*60)
    
    if passed == total:
        print("\n✓✓✓ ALL TESTS PASSED - READY FOR LAUNCH ✓✓✓\n")
        return 0
    else:
        print(f"\n✗✗✗ {total - passed} TEST(S) FAILED ✗✗✗\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
