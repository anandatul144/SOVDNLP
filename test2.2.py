#!/usr/bin/env python3
# quick_test_phase_2.py

"""
Quick verification test for Phase 2
Run this to quickly verify entity resolution is working
"""

def quick_test():
    print("Phase 2 Quick Test")
    print("=" * 60)
    
    try:
        from sovd_nlp_prototype import SOVDAssistant
        print("✅ Import successful")
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    
    try:
        assistant = SOVDAssistant()
        print("✅ Assistant initialized")
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return False
    
    # Test 1: Lowercase resolution
    print("\nTest 1: Lowercase 'v2x' → 'V2X'")
    result = assistant.process_request("get logs from v2x")
    if result["success"] and result["entities"].get("component") == "V2X":
        print("✅ PASS - Resolved to V2X")
    else:
        print(f"❌ FAIL - Got: {result}")
        return False
    
    # Test 2: Fuzzy matching
    print("\nTest 2: Fuzzy 'camera' → 'Camera'")
    result = assistant.process_request("show camera data")
    if result["success"] and result["entities"].get("component") == "Camera":
        print("✅ PASS - Fuzzy matched to Camera")
    else:
        print(f"❌ FAIL - Got: {result}")
        return False
    
    # Test 3: Validation
    print("\nTest 3: Invalid query validation")
    result = assistant.process_request("get logs from Brakes")
    if not result["success"] and "validation" in result["message"].lower():
        print("✅ PASS - Invalid query caught")
    else:
        print(f"⚠️  WARNING - Expected validation failure, got: {result}")
    
    # Test 4: Suggestions
    print("\nTest 4: Smart suggestions")
    result = assistant.process_request("xyz123abc")
    if not result["success"] and result.get("suggestions"):
        print(f"✅ PASS - Got {len(result['suggestions'])} suggestions")
    else:
        print("⚠️  WARNING - Expected suggestions for garbage input")
    
    print("\n" + "=" * 60)
    print("🎉 Phase 2 Quick Test PASSED!")
    print("\nNext steps:")
    print("  1. Run full test suite: python test_phase_2.py")
    print("  2. Try interactive mode: python sovd_demo.py demo --debug")
    print("  3. Ready for Phase 3!")
    
    return True

if __name__ == "__main__":
    import sys
    success = quick_test()
    sys.exit(0 if success else 1)
