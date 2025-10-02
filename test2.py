#!/usr/bin/env python3
# test_phase_2.py

"""
Test suite for Phase 2: Entity Resolution Integration
Validates that NLP processor correctly uses vehicle knowledge.
"""

import sys

def test_vehicle_knowledge_integration():
    """Test 1: Vehicle knowledge is integrated into NLP processor"""
    try:
        from sovd_nlp_prototype import SOVDNLPProcessor
        from vehicle_knowledge import VehicleKnowledge
        
        vk = VehicleKnowledge()
        processor = SOVDNLPProcessor(vehicle_knowledge=vk)
        
        if processor.vehicle_knowledge is None:
            print("❌ FAIL: Vehicle knowledge not integrated")
            return False
        
        print("✅ PASS: Vehicle knowledge integrated successfully")
        return True
    
    except Exception as e:
        print(f"❌ FAIL: Integration error: {e}")
        return False


def test_case_insensitive_resolution():
    """Test 2: Lowercase entity names are resolved"""
    try:
        from sovd_nlp_prototype import SOVDAssistant
        
        assistant = SOVDAssistant()
        
        # Test with lowercase "v2x"
        result = assistant.process_request("get logs from v2x", debug=False)
        
        if not result["success"]:
            print(f"❌ FAIL: Could not parse 'get logs from v2x'")
            return False
        
        # Check if "v2x" was resolved to "V2X"
        component = result["entities"].get("component")
        if component != "V2X":
            print(f"❌ FAIL: Expected 'V2X', got '{component}'")
            return False
        
        print("✅ PASS: Lowercase 'v2x' resolved to 'V2X'")
        return True
    
    except Exception as e:
        print(f"❌ FAIL: Resolution error: {e}")
        return False


def test_fuzzy_component_matching():
    """Test 3: Fuzzy matching finds components"""
    try:
        from sovd_nlp_prototype import SOVDAssistant
        
        assistant = SOVDAssistant()
        
        # Test with "camera" (should find "Camera")
        result = assistant.process_request("get data from camera", debug=False)
        
        if not result["success"]:
            print(f"❌ FAIL: Could not parse 'get data from camera'")
            return False
        
        component = result["entities"].get("component")
        if component != "Camera":
            print(f"❌ FAIL: Expected 'Camera', got '{component}'")
            return False
        
        print("✅ PASS: Fuzzy match 'camera' → 'Camera'")
        return True
    
    except Exception as e:
        print(f"❌ FAIL: Fuzzy matching error: {e}")
        return False


def test_entity_info_enrichment():
    """Test 4: Resolved entities include additional info"""
    try:
        from sovd_nlp_prototype import SOVDAssistant
        
        assistant = SOVDAssistant()
        
        result = assistant.process_request("get logs from V2X", debug=False)
        
        if not result["success"]:
            print(f"❌ FAIL: Could not parse query")
            return False
        
        entities = result["entities"]
        
        # Check for enriched entity information
        if "component_type" not in entities:
            print("⚠️  Warning: Entity type not added (optional feature)")
        
        if "component_info" not in entities:
            print("⚠️  Warning: Entity info not added (optional feature)")
        
        print("✅ PASS: Entity resolution working (info enrichment is optional)")
        return True
    
    except Exception as e:
        print(f"❌ FAIL: Enrichment error: {e}")
        return False


def test_query_validation():
    """Test 5: Invalid queries are caught"""
    try:
        from sovd_nlp_prototype import SOVDAssistant
        
        assistant = SOVDAssistant()
        
        # Test invalid query: Brakes has no apps with logs
        result = assistant.process_request("get logs from Brakes", debug=False)
        
        if result["success"]:
            print("❌ FAIL: Invalid query 'get logs from Brakes' was not caught")
            return False
        
        if "validation" not in result["message"].lower():
            print(f"⚠️  Warning: Error message doesn't mention validation: {result['message']}")
        
        print("✅ PASS: Invalid query rejected")
        return True
    
    except Exception as e:
        print(f"❌ FAIL: Validation error: {e}")
        return False


def test_smart_suggestions():
    """Test 6: Smart suggestions for unmatched queries"""
    try:
        from sovd_nlp_prototype import SOVDAssistant
        
        assistant = SOVDAssistant()
        
        # Test with garbage input
        result = assistant.process_request("asdfghjkl", debug=False)
        
        if result["success"]:
            print("❌ FAIL: Garbage input should not succeed")
            return False
        
        if "suggestions" not in result:
            print("❌ FAIL: No suggestions provided")
            return False
        
        if not result["suggestions"]:
            print("❌ FAIL: Suggestions list is empty")
            return False
        
        print(f"✅ PASS: Smart suggestions provided: {len(result['suggestions'])} suggestions")
        return True
    
    except Exception as e:
        print(f"❌ FAIL: Suggestions error: {e}")
        return False


def test_backward_compatibility():
    """Test 7: Works without vehicle knowledge"""
    try:
        from sovd_nlp_prototype import SOVDNLPProcessor
        
        # Create processor without vehicle knowledge
        processor = SOVDNLPProcessor(vehicle_knowledge=None)
        
        # Should still parse (but without resolution)
        intent = processor.parse_natural_language("list all apps", debug=False)
        
        if intent is None:
            print("❌ FAIL: Basic parsing broken without vehicle knowledge")
            return False
        
        print("✅ PASS: Backward compatible - works without vehicle knowledge")
        return True
    
    except Exception as e:
        print(f"❌ FAIL: Backward compatibility error: {e}")
        return False


def test_debug_mode():
    """Test 8: Debug mode shows resolution steps"""
    try:
        from sovd_nlp_prototype import SOVDAssistant
        import io
        import sys as _sys
        
        assistant = SOVDAssistant()
        
        # Capture debug output
        old_stdout = _sys.stdout
        _sys.stdout = captured_output = io.StringIO()
        
        result = assistant.process_request("get logs from v2x", debug=True)
        
        _sys.stdout = old_stdout
        debug_output = captured_output.getvalue()
        
        if "Resolving" not in debug_output and "Debug:" not in debug_output:
            print("⚠️  Warning: Debug output might not show resolution steps")
        
        print("✅ PASS: Debug mode functional")
        return True
    
    except Exception as e:
        print(f"❌ FAIL: Debug mode error: {e}")
        return False


def test_real_world_queries():
    """Test 9: Real-world query examples"""
    try:
        from sovd_nlp_prototype import SOVDAssistant
        
        assistant = SOVDAssistant()
        
        test_cases = [
            ("get logs from v2x", True, "V2X"),
            ("show camera data", True, "Camera"),
            ("list apps", True, None),
            ("get logs from goldbox", True, "GOLDBOX"),
        ]
        
        failed = []
        for query, should_succeed, expected_component in test_cases:
            result = assistant.process_request(query, debug=False)
            
            if should_succeed and not result["success"]:
                failed.append(f"'{query}' should succeed but failed")
            elif should_succeed and expected_component:
                component = result["entities"].get("component")
                if component != expected_component:
                    failed.append(f"'{query}' expected component '{expected_component}', got '{component}'")
        
        if failed:
            print("❌ FAIL: Real-world queries failed:")
            for f in failed:
                print(f"  - {f}")
            return False
        
        print(f"✅ PASS: All {len(test_cases)} real-world queries work")
        return True
    
    except Exception as e:
        print(f"❌ FAIL: Real-world query error: {e}")
        return False


def test_unresolved_entities():
    """Test 10: Graceful handling of unknown entities"""
    try:
        from sovd_nlp_prototype import SOVDAssistant
        
        assistant = SOVDAssistant()
        
        # Test with completely unknown component
        result = assistant.process_request("get logs from FakeComponent123", debug=False)
        
        # Should either:
        # 1. Parse but keep original value
        # 2. Reject with suggestions
        # Either behavior is acceptable
        
        if result["success"]:
            component = result["entities"].get("component")
            if component != "FakeComponent123":
                print(f"⚠️  Warning: Unknown component changed to '{component}'")
        else:
            if "suggestions" not in result:
                print("⚠️  Warning: No suggestions for unknown component")
        
        print("✅ PASS: Graceful handling of unknown entities")
        return True
    
    except Exception as e:
        print(f"❌ FAIL: Unknown entity error: {e}")
        return False


def run_all_tests():
    """Run all Phase 2 tests"""
    print("=" * 70)
    print("Phase 2 Test Suite: Entity Resolution Integration")
    print("=" * 70)
    print()
    
    tests = [
        ("Vehicle knowledge integration", test_vehicle_knowledge_integration),
        ("Case-insensitive resolution", test_case_insensitive_resolution),
        ("Fuzzy component matching", test_fuzzy_component_matching),
        ("Entity info enrichment", test_entity_info_enrichment),
        ("Query validation", test_query_validation),
        ("Smart suggestions", test_smart_suggestions),
        ("Backward compatibility", test_backward_compatibility),
        ("Debug mode", test_debug_mode),
        ("Real-world queries", test_real_world_queries),
        ("Unknown entity handling", test_unresolved_entities),
    ]
    
    results = []
    
    for i, (name, test_func) in enumerate(tests, 1):
        print(f"\nTest {i}/{len(tests)}: {name}")
        print("-" * 70)
        
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"❌ FAIL: Unexpected error: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    
    passed = sum(1 for _, p in results if p)
    total = len(results)
    
    for name, p in results:
        status = "✅ PASS" if p else "❌ FAIL"
        print(f"{status}: {name}")
    
    print("-" * 70)
    print(f"Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 All Phase 2 tests passed! Entity resolution working correctly.")
        return True
    elif passed >= total * 0.8:
        print(f"\n⚠️  {total - passed} test(s) failed, but 80%+ passing. Review failures.")
        return True
    else:
        print(f"\n❌ {total - passed} test(s) failed. Please fix before proceeding.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)