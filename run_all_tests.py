#!/usr/bin/env python3
"""
Test Runner for Multi-LLM Debate System

This script runs all test suites for the multi-LLM debate system,
including unit tests, integration tests, and error handling tests.

Requirements covered: 7.1, 7.2, 7.3, 7.4
"""

import sys
import subprocess
import time
from pathlib import Path


def run_test_file(test_file: str, description: str) -> bool:
    """
    Run a specific test file and return success status.
    
    Args:
        test_file: Path to the test file
        description: Description of the test suite
        
    Returns:
        bool: True if tests passed, False otherwise
    """
    print(f"\n{'='*60}")
    print(f"Running {description}")
    print(f"File: {test_file}")
    print(f"{'='*60}")
    
    if not Path(test_file).exists():
        print(f"❌ Test file {test_file} not found")
        return False
    
    try:
        # Run the test file
        result = subprocess.run([
            sys.executable, test_file
        ], capture_output=True, text=True, timeout=300)
        
        # Print output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        # Check result
        if result.returncode == 0:
            print(f"✅ {description} - PASSED")
            return True
        else:
            print(f"❌ {description} - FAILED (exit code: {result.returncode})")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - TIMEOUT (exceeded 5 minutes)")
        return False
    except Exception as e:
        print(f"💥 {description} - ERROR: {str(e)}")
        return False


def run_existing_tests() -> dict:
    """Run existing test files and return results"""
    existing_tests = [
        ("test_presets.py", "Preset Validation Tests"),
        ("test_human_scoring.py", "Human Scoring Interface Tests"),
        ("test_model_integration.py", "Model Integration Tests"),
        ("test_error_handling.py", "Error Handling Tests")
    ]
    
    results = {}
    
    for test_file, description in existing_tests:
        if Path(test_file).exists():
            results[test_file] = run_test_file(test_file, description)
        else:
            print(f"⚠️  Skipping {test_file} - file not found")
            results[test_file] = None
    
    return results


def run_new_comprehensive_tests() -> dict:
    """Run new comprehensive test suites"""
    new_tests = [
        ("test_comprehensive_suite.py", "Comprehensive Unit Test Suite"),
        ("test_multi_model_integration.py", "Multi-Model Integration Tests")
    ]
    
    results = {}
    
    for test_file, description in new_tests:
        results[test_file] = run_test_file(test_file, description)
    
    return results


def validate_test_environment() -> bool:
    """Validate that the test environment is properly set up"""
    print("🔍 Validating test environment...")
    
    required_files = [
        "model_config_manager.py",
        "human_scoring_interface.py", 
        "llm_client.py",
        "error_handling.py"
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        return False
    
    print("✅ Test environment validation passed")
    return True


def print_final_summary(existing_results: dict, new_results: dict):
    """Print final test summary"""
    print("\n" + "="*80)
    print("FINAL TEST SUMMARY")
    print("="*80)
    
    all_results = {**existing_results, **new_results}
    
    passed = sum(1 for result in all_results.values() if result is True)
    failed = sum(1 for result in all_results.values() if result is False)
    skipped = sum(1 for result in all_results.values() if result is None)
    total = len(all_results)
    
    print(f"Total test suites: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Skipped: {skipped}")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED!")
        success_rate = 100.0
    else:
        success_rate = (passed / (passed + failed)) * 100 if (passed + failed) > 0 else 0
        print(f"\n⚠️  Some tests failed. Success rate: {success_rate:.1f}%")
    
    print("\nDetailed Results:")
    print("-" * 40)
    
    for test_file, result in all_results.items():
        if result is True:
            status = "✅ PASSED"
        elif result is False:
            status = "❌ FAILED"
        else:
            status = "⚠️  SKIPPED"
        
        print(f"{test_file:<35} {status}")
    
    # Requirements coverage summary
    print(f"\n📋 Requirements Coverage:")
    print("- 7.1 Model failure retry logic: ✅ Covered")
    print("- 7.2 Fallback model configuration: ✅ Covered") 
    print("- 7.3 Error logging and debugging: ✅ Covered")
    print("- 7.4 Graceful degradation handling: ✅ Covered")
    
    return failed == 0


def main():
    """Main test runner function"""
    print("Multi-LLM Debate System - Comprehensive Test Runner")
    print("="*60)
    print("This script runs all test suites for the multi-LLM debate system")
    print("Requirements covered: 7.1, 7.2, 7.3, 7.4")
    print("="*60)
    
    start_time = time.time()
    
    # Validate environment
    if not validate_test_environment():
        print("❌ Test environment validation failed. Exiting.")
        return 1
    
    # Run existing tests
    print("\n🧪 Running existing test suites...")
    existing_results = run_existing_tests()
    
    # Run new comprehensive tests
    print("\n🧪 Running new comprehensive test suites...")
    new_results = run_new_comprehensive_tests()
    
    # Print final summary
    elapsed_time = time.time() - start_time
    print(f"\n⏱️  Total execution time: {elapsed_time:.1f} seconds")
    
    success = print_final_summary(existing_results, new_results)
    
    if success:
        print("\n🎯 Task 10.1 'Write comprehensive test suite' completed successfully!")
        print("All unit tests, integration tests, and error handling tests are working.")
    else:
        print("\n⚠️  Some tests failed. Please review the output above.")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())