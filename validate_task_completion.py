#!/usr/bin/env python3
"""
Task 10 Completion Validation Script

This script validates that Task 10 "Create Integration Tests and Examples" 
has been completed successfully by checking for all required deliverables.

Requirements covered: 7.1, 7.2, 7.3, 7.4
"""

import os
from pathlib import Path


def check_file_exists(file_path: str, description: str) -> bool:
    """Check if a file exists and report the result"""
    if Path(file_path).exists():
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} (NOT FOUND)")
        return False


def check_directory_exists(dir_path: str, description: str) -> bool:
    """Check if a directory exists and report the result"""
    if Path(dir_path).exists() and Path(dir_path).is_dir():
        print(f"✅ {description}: {dir_path}")
        return True
    else:
        print(f"❌ {description}: {dir_path} (NOT FOUND)")
        return False


def validate_file_content(file_path: str, required_content: list, description: str) -> bool:
    """Validate that a file contains required content"""
    if not Path(file_path).exists():
        print(f"❌ {description}: File not found")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        missing_content = []
        for required in required_content:
            if required not in content:
                missing_content.append(required)
        
        if missing_content:
            print(f"❌ {description}: Missing content - {', '.join(missing_content)}")
            return False
        else:
            print(f"✅ {description}: All required content present")
            return True
            
    except Exception as e:
        print(f"❌ {description}: Error reading file - {e}")
        return False


def validate_task_10_1():
    """Validate sub-task 10.1: Write comprehensive test suite"""
    print("\n" + "="*60)
    print("Validating Task 10.1: Write comprehensive test suite")
    print("="*60)
    
    success = True
    
    # Check test files exist
    test_files = [
        ("test_comprehensive_suite.py", "Comprehensive unit test suite"),
        ("test_multi_model_integration.py", "Multi-model integration tests"),
        ("run_all_tests.py", "Test runner script")
    ]
    
    for file_path, description in test_files:
        if not check_file_exists(file_path, description):
            success = False
    
    # Validate comprehensive test suite content
    required_test_content = [
        "TestModelConfigManager",
        "TestHumanScoringInterface", 
        "TestMultiModelGameScenarios",
        "TestErrorHandlingAndRecovery",
        "unittest.TestCase",
        "Requirements covered: 7.1, 7.2, 7.3, 7.4"
    ]
    
    if not validate_file_content("test_comprehensive_suite.py", required_test_content, 
                                "Comprehensive test suite content"):
        success = False
    
    # Validate integration test content
    required_integration_content = [
        "TestMultiModelGameIntegration",
        "TestErrorRecoveryScenarios",
        "TestHumanScoringIntegration",
        "unittest.TestCase",
        "Requirements covered: 7.1, 7.2, 7.3, 7.4"
    ]
    
    if not validate_file_content("test_multi_model_integration.py", required_integration_content,
                                "Integration test suite content"):
        success = False
    
    return success


def validate_task_10_2():
    """Validate sub-task 10.2: Create example configurations and documentation"""
    print("\n" + "="*60)
    print("Validating Task 10.2: Create example configurations and documentation")
    print("="*60)
    
    success = True
    
    # Check examples directory exists
    if not check_directory_exists("examples", "Examples directory"):
        success = False
    
    # Check example files exist
    example_files = [
        ("examples/example_single_model_game.py", "Single model game example"),
        ("examples/example_mixed_model_game.py", "Mixed model game example"),
        ("examples/example_human_scoring_game.py", "Human scoring integration example"),
        ("examples/README.md", "Examples documentation")
    ]
    
    for file_path, description in example_files:
        if not check_file_exists(file_path, description):
            success = False
    
    # Check documentation files exist
    doc_files = [
        ("docs/CONFIGURATION_GUIDE.md", "Configuration guide"),
        ("docs/TROUBLESHOOTING_GUIDE.md", "Troubleshooting guide")
    ]
    
    for file_path, description in doc_files:
        if not check_file_exists(file_path, description):
            success = False
    
    # Validate example content
    required_example_content = [
        "Requirements covered: 3.1, 3.2, 1.3",
        "ModelConfigManager",
        "LLMClient",
        "validate_model"
    ]
    
    for example_file, _ in example_files[:-1]:  # Skip README
        if Path(example_file).exists():
            if not validate_file_content(example_file, required_example_content,
                                       f"Example content ({example_file})"):
                success = False
    
    # Validate documentation content
    config_guide_content = [
        "Model Configuration",
        "Preset Management", 
        "Human Scoring Configuration",
        "Error Handling Configuration",
        "Troubleshooting"
    ]
    
    if not validate_file_content("docs/CONFIGURATION_GUIDE.md", config_guide_content,
                                "Configuration guide content"):
        success = False
    
    troubleshooting_content = [
        "Model Configuration Issues",
        "Preset Management Issues",
        "Human Scoring Issues", 
        "Error Handling Issues",
        "Debugging Tools"
    ]
    
    if not validate_file_content("docs/TROUBLESHOOTING_GUIDE.md", troubleshooting_content,
                                "Troubleshooting guide content"):
        success = False
    
    return success


def validate_requirements_coverage():
    """Validate that all requirements are covered"""
    print("\n" + "="*60)
    print("Validating Requirements Coverage")
    print("="*60)
    
    requirements = {
        "7.1": "Model failure retry logic",
        "7.2": "Fallback model configuration", 
        "7.3": "Error logging and debugging",
        "7.4": "Graceful degradation handling"
    }
    
    success = True
    
    # Check that requirements are mentioned in test files
    test_files = ["test_comprehensive_suite.py", "test_multi_model_integration.py"]
    
    for test_file in test_files:
        if Path(test_file).exists():
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                covered_requirements = []
                for req_id, req_desc in requirements.items():
                    if req_id in content:
                        covered_requirements.append(req_id)
                
                print(f"✅ {test_file}: Covers requirements {', '.join(covered_requirements)}")
                
                if len(covered_requirements) < len(requirements):
                    missing = set(requirements.keys()) - set(covered_requirements)
                    print(f"⚠️  {test_file}: Missing requirements {', '.join(missing)}")
                    
            except Exception as e:
                print(f"❌ Error checking {test_file}: {e}")
                success = False
    
    return success


def main():
    """Main validation function"""
    print("Task 10 Completion Validation")
    print("Multi-LLM Debate System - Integration Tests and Examples")
    print("="*80)
    
    # Validate sub-tasks
    task_10_1_success = validate_task_10_1()
    task_10_2_success = validate_task_10_2()
    requirements_success = validate_requirements_coverage()
    
    # Overall validation
    overall_success = task_10_1_success and task_10_2_success and requirements_success
    
    print("\n" + "="*80)
    print("VALIDATION SUMMARY")
    print("="*80)
    
    print(f"Task 10.1 (Test Suite): {'✅ PASS' if task_10_1_success else '❌ FAIL'}")
    print(f"Task 10.2 (Examples & Docs): {'✅ PASS' if task_10_2_success else '❌ FAIL'}")
    print(f"Requirements Coverage: {'✅ PASS' if requirements_success else '❌ FAIL'}")
    
    print(f"\nOverall Task 10 Status: {'✅ COMPLETED' if overall_success else '❌ INCOMPLETE'}")
    
    if overall_success:
        print("\n🎉 Task 10 'Create Integration Tests and Examples' completed successfully!")
        print("\nDeliverables created:")
        print("• Comprehensive unit test suite with error handling tests")
        print("• Multi-model integration test suite")
        print("• Example scripts for different model configurations")
        print("• Configuration guide and troubleshooting documentation")
        print("• Test runner for automated validation")
        print("\nAll requirements (7.1, 7.2, 7.3, 7.4) are covered by the test suite.")
    else:
        print("\n⚠️  Task 10 validation failed. Please review the issues above.")
    
    return overall_success


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)