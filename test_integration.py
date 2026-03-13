#!/usr/bin/env python3
"""
Integration test for cyberpunk navigator
Tests the full pipeline without user interaction
"""

import sys
sys.path.insert(0, 'D:\\robot-navigation')

def test_full_pipeline():
    """Test the complete navigation pipeline"""
    print("\n" + "="*70)
    print("CYBERPUNK NAVIGATOR - FULL PIPELINE TEST")
    print("="*70 + "\n")
    
    try:
        from navigator import (
            Navigator, GameConfig, Difficulty, Speed, 
            Grid, GameState, AStar, FogOfWar
        )
        
        # Step 1: Create config
        print("[1/6] Creating game configuration...")
        config = GameConfig(
            difficulty=Difficulty.EASY,
            speed=Speed.FAST,
            grid_size=15,
            sensor_range=3
        )
        print("      ✓ Config created")
        
        # Step 2: Create grid
        print("[2/6] Generating grid with obstacles...")
        grid = Grid(size=config.grid_size, obstacle_percentage=config.difficulty.value)
        grid.place_obstacles()
        print(f"      ✓ Grid created (15x15)")
        
        # Step 3: Initialize game state
        print("[3/6] Initializing game state...")
        game_state = GameState(grid, config)
        print(f"      ✓ Game state initialized")
        
        # Step 4: Run A* pathfinding
        print("[4/6] Running A* pathfinding...")
        astar = AStar(grid)
        path, metrics = astar.find_path()
        game_state.set_path(path)
        game_state.metrics = metrics
        print(f"      ✓ Path found: {len(path)} steps")
        print(f"      ✓ Nodes explored: {metrics.nodes_explored}")
        print(f"      ✓ Efficiency: {metrics.efficiency:.2f}%")
        print(f"      ✓ Computation time: {metrics.computation_time_ms:.2f}ms")
        
        # Step 5: Initialize fog of war
        print("[5/6] Setting up fog of war...")
        fog_of_war = FogOfWar(grid, sensor_range=config.sensor_range)
        fog_of_war.reveal_around(*grid.start_pos)
        game_state.discovered_tiles = fog_of_war.discovered_tiles.copy()
        print(f"      ✓ Fog of war initialized (sensor range: {config.sensor_range})")
        
        # Step 6: Create Navigator and test rendering
        print("[6/6] Initializing Navigator and testing rendering...")
        navigator = Navigator()
        navigator.config = config
        navigator.grid = grid
        navigator.game_state = game_state
        navigator.astar = astar
        navigator.fog_of_war = fog_of_war
        navigator._spawn_hazards()
        
        print(f"      ✓ Navigator created with {len(navigator.hazards)} hazards")
        
        # Test rendering functions
        print("\n" + "-"*70)
        print("RENDERING TESTS")
        print("-"*70)
        
        try:
            # Test grid rendering
            print("[R1] Testing grid rendering...")
            grid_render = navigator.render_grid()
            assert grid_render != ""
            assert len(grid_render.split('\n')) == 15
            print(f"      ✓ Grid rendered ({len(grid_render)} chars)")
            
            # Test hex stream
            print("[R2] Testing hex stream rendering...")
            hex_stream = navigator.render_hex_stream()
            assert hex_stream != ""
            print(f"      ✓ Hex stream rendered")
            
            # Test bar charts
            print("[R3] Testing bar chart rendering...")
            bar_charts = navigator.render_bar_charts()
            assert "PROGRESS" in bar_charts
            print(f"      ✓ Bar charts rendered")
            
            # Test telemetry bar
            print("[R4] Testing telemetry bar...")
            telemetry = navigator.render_telemetry_bar()
            assert "SATELLITE LINK" in telemetry
            print(f"      ✓ Telemetry bar rendered")
            
            # Test sidebar
            print("[R5] Testing sidebar rendering...")
            sidebar = navigator.render_sidebar()
            assert "TELEMETRY" in str(sidebar)
            print(f"      ✓ Sidebar rendered")
            
            # Test layout
            print("[R6] Testing display layout...")
            layout = navigator.render_display()
            assert layout is not None
            print(f"      ✓ Layout created")
            
            # Test effects
            print("[R7] Testing effect updates...")
            navigator._update_effects()
            assert navigator.animation_state.frame_count > 0
            print(f"      ✓ Effects updated (frame {navigator.animation_state.frame_count})")
            
            print("\n" + "="*70)
            print("✓✓✓ ALL TESTS PASSED - SYSTEM READY FOR LAUNCH ✓✓✓")
            print("="*70 + "\n")
            return 0
            
        except AssertionError as ae:
            print(f"      ✗ Assertion failed: {ae}")
            return 1
        except Exception as re:
            print(f"      ✗ Rendering error: {re}")
            import traceback
            traceback.print_exc()
            return 1
        
    except Exception as e:
        print(f"✗ Pipeline error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(test_full_pipeline())
