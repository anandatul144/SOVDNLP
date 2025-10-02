#!/usr/bin/env python3
# test_context_aware.py

"""
Test context-aware app resolution.
Tests the fixes for compound app names and component-scoped searches.
"""

from sovd_nlp_prototype import SOVDAssistant

def test_queries():
    """Test the problematic queries from manual testing"""
    
    assistant = SOVDAssistant()
    
    print("Context-Aware App Resolution Tests")
    print("=" * 70)
    
    test_cases = [
        # Issue 1: List apps on component
        {
            "query": "list apps in V2X",
            "expected_intent": "list_apps_on_component",
            "expected_component": "V2X",
            "description": "List apps on specific component"
        },
        
        # Issue 2: V2X HIDS with context
        {
            "query": "list V2X hids logs",
            "expected_intent": "get_bulk_data",
            "expected_app": "V2X_HIDS",
            "description": "V2X + hids should find V2X_HIDS"
        },
        
        # Issue 3: Switch NIDS with context
        {
            "query": "get switch nids alerts",
            "expected_intent": "get_bulk_data",
            "expected_app": "NIDS_Suricata",
            "description": "Switch + nids should find NIDS_Suricata"
        },
        
        # Issue 4: GOLDBOX IDS with context
        {
            "query": "get goldbox ids logs",
            "expected_intent": "get_bulk_data",
            "expected_app": "GOLDBOX_IDS",
            "description": "GOLDBOX + ids should find GOLDBOX_IDS"
        },
        
        # Baseline: Simple queries should still work
        {
            "query": "list apps",
            "expected_intent": "list_apps",
            "description": "List all apps (no component)"
        },
        {
            "query": "get v2x logs",
            "expected_intent": "get_logs",
            "expected_component": "V2X",
            "description": "Component logs still work"
        },
    ]
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test['description']}")
        print(f"Query: '{test['query']}'")
        
        result = assistant.process_request(test['query'], debug=False)
        
        if not result["success"]:
            print(f"  ❌ FAIL: Query failed - {result['message']}")
            failed += 1
            continue
        
        # Check intent
        if result["intent"] != test["expected_intent"]:
            print(f"  ❌ FAIL: Expected intent '{test['expected_intent']}', got '{result['intent']}'")
            failed += 1
            continue
        
        # Check component if expected
        if "expected_component" in test:
            component = result["entities"].get("component")
            if component != test["expected_component"]:
                print(f"  ❌ FAIL: Expected component '{test['expected_component']}', got '{component}'")
                failed += 1
                continue
        
        # Check app if expected
        if "expected_app" in test:
            app = result["entities"].get("app")
            if app != test["expected_app"]:
                print(f"  ❌ FAIL: Expected app '{test['expected_app']}', got '{app}'")
                failed += 1
                continue
        
        print(f"  ✅ PASS")
        if "expected_app" in test:
            print(f"     App: {result['entities'].get('app')}")
        if "expected_component" in test:
            print(f"     Component: {result['entities'].get('component')}")
        
        passed += 1
    
    print("\n" + "=" * 70)
    print(f"Results: {passed}/{len(test_cases)} passed")
    
    if passed == len(test_cases):
        print("\n🎉 All context-aware tests passed!")
        print("\nNow working:")
        print("  ✅ list apps in V2X")
        print("  ✅ list V2X hids logs")
        print("  ✅ get switch nids alerts")
        print("  ✅ get goldbox ids logs")
    else:
        print(f"\n⚠️  {failed} test(s) failed")
    
    return passed == len(test_cases)

if __name__ == "__main__":
    import sys
    success = test_queries()
    sys.exit(0 if success else 1)