#!/usr/bin/env python3
"""
Comprehensive test of the professional navigator
"""
import ast
import sys
import os

# Change to the robot-navigation directory
os.chdir('D:\\robot-navigation')

print("=" * 60)
print("PROFESSIONAL NAVIGATOR - SYNTAX & IMPORT TEST")
print("=" * 60)

# Step 1: Syntax check
print("\n[1/3] Checking syntax...")
try:
    with open('navigator_professional.py', 'r') as f:
        code = f.read()
    ast.parse(code)
    print("      ✓ Syntax is valid")
except SyntaxError as e:
    print(f"      ✗ Syntax error: {e}")
    sys.exit(1)

# Step 2: Import check
print("\n[2/3] Importing module...")
try:
    import navigator_professional as nav
    print("      ✓ Module imported successfully")
except Exception as e:
    print(f"      ✗ Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 3: Component verification
print("\n[3/3] Verifying components...")
components = [
    'Difficulty', 'Speed', 'GridConfig', 'Point',
    'SimulationState', 'NavigationGrid', 'DashboardRenderer',
    'MenuSystem', 'RobotNavigationSimulator', 'ProfessionalTheme'
]

all_good = True
for component in components:
    if hasattr(nav, component):
        print(f"      ✓ {component}")
    else:
        print(f"      ✗ {component} NOT FOUND")
        all_good = False

if not all_good:
    sys.exit(1)

# Quick functionality test
print("\n[BONUS] Quick functionality test...")
try:
    # Create a small grid
    config = nav.GridConfig(size=8, difficulty=nav.Difficulty.MEDIUM)
    grid = nav.NavigationGrid(config)
    print(f"      ✓ Grid created: {grid.size}×{grid.size}")
    
    # Test pathfinding
    path = grid.calculate_path_astar()
    if path and len(path) > 0:
        print(f"      ✓ A* pathfinding: {len(path)} nodes found")
    else:
        print(f"      ✗ A* pathfinding returned empty path")
        sys.exit(1)
    
    # Test state
    state = nav.SimulationState()
    print(f"      ✓ SimulationState initialized")
    
    # Test theme
    print(f"      ✓ Theme colors: {nav.ProfessionalTheme.CYAN}")
    
except Exception as e:
    print(f"      ✗ Functionality test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ ALL TESTS PASSED - READY TO RUN!")
print("=" * 60)
print("\nTo run the simulator, execute:")
print("  python navigator_professional.py")
