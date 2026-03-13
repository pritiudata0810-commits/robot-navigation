#!/usr/bin/env python3
"""
Final validation: Verify all cyberpunk features are implemented
Checks source code for presence of required elements
"""

import re
import sys

def check_file_for_features():
    """Check navigator.py for all required cyberpunk features"""
    
    with open('D:\\robot-navigation\\navigator.py', 'r') as f:
        content = f.read()
    
    features = {
        # Core classes
        "CyberpunkTheme class": r"class CyberpunkTheme",
        "AnimationState class": r"class AnimationState",
        "Hazard class": r"class Hazard",
        
        # Colors
        "Neon Cyan color": r"#00FFFF",
        "Magenta color": r"#FF00FF",
        "Neon Green color": r"#00FF00",
        "Deep Purple color": r"#330033",
        "Red Alert color": r"#FF0000",
        "Yellow flicker color": r"#FFFF00",
        
        # 3-column layout
        "Three-column split": r'split_row.*"left".*"center".*"right"',
        "Hex stream panel": r"HEX STREAM",
        "Sector map panel": r"SECTOR MAP",
        "Telemetry panel": r"TELEMETRY",
        
        # Visual effects
        "Radar pulse": r"pulse_radius",
        "Particle trails": r"particle_trails",
        "Heatmap system": r"self\.heatmap",
        "Search frontier": r"search_frontier",
        "Scanline overlay": r"scanline",
        "Glitch borders": r"border_style",
        
        # Telemetry
        "Satellite link": r"SATELLITE LINK",
        "CPU load": r"CPU",
        "Coordinate mapping": r"COORDINATE MAPPING",
        "Red alert system": r"RED ALERT",
        
        # Rendering functions
        "Hex stream renderer": r"def render_hex_stream",
        "Bar chart renderer": r"def render_bar_charts",
        "Telemetry renderer": r"def render_telemetry_bar",
        "Grid renderer": r"def render_grid",
        "Display layout": r"def render_display",
        
        # Animation
        "Effect updates": r"def _update_effects",
        "50ms frame timing": r"frame_delay = 0\.05",
        "Animation loop": r"while not self\.game_state\.is_finished",
        
        # Hazards
        "Hazard spawning": r"def _spawn_hazards",
        "Hazard movement": r"hazard\.update",
        "Collision detection": r"distance_to",
        
        # Success screen
        "SYSTEM CLEAR banner": r"SYSTEM CLEAR",
        "Success celebration": r"_show_success_celebration",
        "Mission summary": r"MISSION SUMMARY",
    }
    
    print("\n" + "="*70)
    print("CYBERPUNK NAVIGATOR - FEATURE VALIDATION")
    print("="*70 + "\n")
    
    found = 0
    missing = 0
    
    for feature_name, pattern in features.items():
        if re.search(pattern, content, re.IGNORECASE | re.DOTALL):
            print(f"✓ {feature_name}")
            found += 1
        else:
            print(f"✗ {feature_name}")
            missing += 1
    
    print("\n" + "="*70)
    print(f"RESULTS: {found}/{found + missing} features found")
    print("="*70 + "\n")
    
    if missing == 0:
        print("✓✓✓ ALL FEATURES IMPLEMENTED ✓✓✓\n")
        return 0
    else:
        print(f"✗✗✗ {missing} FEATURE(S) MISSING ✗✗✗\n")
        return 1

if __name__ == "__main__":
    sys.exit(check_file_for_features())
