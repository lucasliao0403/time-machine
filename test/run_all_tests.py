"""
Test runner for all TimeMachine tests
Runs all test files and provides a summary
"""
import os
import sys
import subprocess
from pathlib import Path

def run_test_file(test_file):
    """Run a single test file and capture results"""
    print(f"\n{'='*60}")
    print(f"RUNNING: {test_file}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            [sys.executable, test_file],
            cwd=Path(__file__).parent.parent,  # Run from project root
            capture_output=True,
            text=True,
            timeout=60
        )
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        # Check if test passed based on exit code and output
        passed = result.returncode == 0 and ("[PASS]" in result.stdout or "PASSED" in result.stdout)
        
        return passed, result.stdout, result.stderr
    
    except subprocess.TimeoutExpired:
        print("[FAIL] Test timed out")
        return False, "", "Test timed out"
    except Exception as e:
        print(f"[FAIL] Test failed to run: {e}")
        return False, "", str(e)

def main():
    """Run all tests and provide summary"""
    print("[TEST] TimeMachine Test Suite Runner")
    print("=" * 60)
    
    # Get all test files
    test_dir = Path(__file__).parent
    test_files = [
        "test/test_basic_functionality.py",
        "test/test_serialization.py", 
        "test/test_decorator_integration.py",
        "test/test_context_manager.py",
        "test/test_demo_sample_agent.py"
    ]
    
    results = {}
    
    for test_file in test_files:
        passed, stdout, stderr = run_test_file(test_file)
        results[test_file] = {
            'passed': passed,
            'stdout': stdout,
            'stderr': stderr
        }
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    
    total_tests = len(test_files)
    passed_tests = sum(1 for r in results.values() if r['passed'])
    
    for test_file, result in results.items():
        status = "[PASS] PASSED" if result['passed'] else "[FAIL] FAILED"
        print(f"{status:12} {test_file}")
    
    print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n[SUCCESS] ALL TESTS PASSED! TimeMachine is working correctly.")
        return True
    else:
        print(f"\n[WARNING] {total_tests - passed_tests} test(s) failed. Check output above for details.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
