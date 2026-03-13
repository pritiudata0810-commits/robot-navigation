#!/usr/bin/env python3
"""Quick test to verify navigator module loads"""

if __name__ == "__main__":
    try:
        from navigator import Navigator, CyberpunkTheme, AnimationState, Hazard
        print("✓ All imports successful")
        
        # Test theme
        print(f"✓ Theme CYAN: {CyberpunkTheme.CYAN}")
        print(f"✓ Depth color: {CyberpunkTheme.depth_color(1)}")
        
        # Test animation state
        anim = AnimationState()
        anim.tick(50)
        print(f"✓ Animation state ticked: frame={anim.frame_count}")
        
        # Test hazard
        h = Hazard(5.0, 5.0, 0.1, 0.2)
        h.update(15)
        print(f"✓ Hazard updated: pos=({h.x}, {h.y})")
        
        print("\n✓✓✓ All basic tests passed! ✓✓✓")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
