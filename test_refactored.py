"""
Quick validation script for refactored navigator_professional.py
Checks for syntax errors and critical functionality
"""

import sys
import ast

def check_syntax():
    """Validate Python syntax"""
    try:
        with open('navigator_professional.py', 'r') as f:
            code = f.read()
        ast.parse(code)
        print("✓ Syntax validation: PASSED")
        return True
    except SyntaxError as e:
        print(f"✗ Syntax Error: {e}")
        return False

def check_imports():
    """Verify required imports"""
    required_imports = [
        'random',
        'time',
        'heapq',
        'Console',
        'Live',
        'Table',
        'Panel',
        'Layout',
        'Text',
        'Columns',
        'Align',
        'Prompt'
    ]
    
    with open('navigator_professional.py', 'r') as f:
        content = f.read()
    
    missing = []
    for imp in required_imports:
        if imp not in content:
            missing.append(imp)
    
    if not missing:
        print("✓ Import validation: PASSED")
        return True
    else:
        print(f"✗ Missing imports: {missing}")
        return False

def check_classes():
    """Verify all required classes exist"""
    required_classes = [
        'Difficulty',
        'Speed',
        'ProfessionalTheme',
        'Point',
        'GridConfig',
        'SimulationState',
        'NavigationGrid',
        'DashboardRenderer',
        'MenuSystem',
        'RobotNavigationSimulator'
    ]
    
    with open('navigator_professional.py', 'r') as f:
        content = f.read()
    
    missing = []
    for cls in required_classes:
        if f"class {cls}" not in content:
            missing.append(cls)
    
    if not missing:
        print("✓ Class definition validation: PASSED")
        return True
    else:
        print(f"✗ Missing classes: {missing}")
        return False

def check_key_features():
    """Verify key refactoring features"""
    features = {
        'Header display': 'def display_header',
        'Prompt import': 'from rich.prompt import Prompt',
        'Columns layout': 'Columns([logs_panel, grid_panel, telemetry_panel]',
        'Underscore empty cells': '"_  "',
        'Live update loop': 'live.update(self.renderer.render_dashboard',
        'Direction logging (uppercase)': '"LEFT", "RIGHT", "UP", "DOWN"',
        'Path efficiency metric': '"Shortest Path Efficiency"',
        'Replay loop': 'while True:',
        'Render mission success': 'def render_mission_success',
        'A* pathfinding': 'def calculate_path_astar'
    }
    
    with open('navigator_professional.py', 'r') as f:
        content = f.read()
    
    missing = []
    for feature, check_str in features.items():
        if check_str not in content:
            missing.append(feature)
    
    if not missing:
        print("✓ Key features validation: PASSED")
        return True
    else:
        print(f"✗ Missing features: {missing}")
        return False

def main():
    """Run all validation checks"""
    print("=" * 60)
    print("NAVIGATOR PROFESSIONAL - REFACTORING VALIDATION")
    print("=" * 60)
    print()
    
    results = []
    
    # Run checks
    print("[1/4] Checking syntax...")
    results.append(check_syntax())
    
    print("[2/4] Checking imports...")
    results.append(check_imports())
    
    print("[3/4] Checking class definitions...")
    results.append(check_classes())
    
    print("[4/4] Checking key features...")
    results.append(check_key_features())
    
    print()
    print("=" * 60)
    
    if all(results):
        print("✓ ALL VALIDATION CHECKS PASSED")
        print("=" * 60)
        return 0
    else:
        passed = sum(results)
        total = len(results)
        print(f"✗ VALIDATION FAILED ({passed}/{total} checks passed)")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
