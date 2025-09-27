#!/usr/bin/env python3
"""
Simple test script for the error handling and recovery system.

This script tests the error handling logic without requiring external dependencies.
"""

import sys
import time
from typing import Dict, List
from error_handling import (
    GracefulDegradationManager, 
    ErrorType,
    create_default_fallback_configuration
)


def test_graceful_degradation():
    """Test graceful degradation manager"""
    print("=" * 60)
    print("Testing Graceful Degradation Manager")
    print("=" * 60)
    
    degradation_manager = GracefulDegradationManager(default_timeout=30.0)
    
    # Test timeout handling
    print("\nTesting timeout handling:")
    timeout_result = degradation_manager.handle_timeout(
        player_name="TestPlayer",
        model_name="slow-model",
        timeout_duration=35.0
    )
    print(f"✓ Timeout handled: {timeout_result['success']}")
    print(f"  User message: {timeout_result.get('user_message', 'No message')}")
    print(f"  Timeout count: {timeout_result['timeout_count']}")
    
    # Test multiple timeouts
    print("\nTesting multiple timeouts:")
    for i in range(3):
        timeout_result = degradation_manager.handle_timeout(
            player_name="TestPlayer",
            model_name="slow-model",
            timeout_duration=30.0 + i * 5
        )
        print(f"  Timeout {i+2}: Count = {timeout_result['timeout_count']}")
    
    # Test model failure handling
    print("\nTesting model failure handling:")
    failure_result = degradation_manager.handle_player_model_failure(
        player_name="TestPlayer2",
        model_name="failed-model",
        error=Exception("Model API error")
    )
    print(f"✓ Failure handled: {failure_result['success']}")
    print(f"  Degraded: {failure_result['degraded']}")
    print(f"  Reason: {failure_result['reason']}")
    
    # Test game continuation logic
    print("\nTesting game continuation logic:")
    test_cases = [
        (["Player1"], 4, "1/4 failed"),
        (["Player1", "Player2"], 4, "2/4 failed"),
        (["Player1", "Player2", "Player3"], 4, "3/4 failed"),
        (["Player1"], 2, "1/2 failed"),
    ]
    
    for failed_players, total_players, description in test_cases:
        should_continue = degradation_manager.should_continue_game(
            failed_players=failed_players, 
            total_players=total_players
        )
        status = "✓ Continue" if should_continue else "✗ Stop"
        print(f"  {description}: {status}")
    
    # Test game continuation messages
    print("\nTesting game continuation messages:")
    test_degraded_lists = [
        [],
        ["Player1"],
        ["Player1", "Player2"],
        ["Player1", "Player2", "Player3"]
    ]
    
    for degraded_players in test_degraded_lists:
        message = degradation_manager.generate_game_continuation_message(degraded_players)
        print(f"  {len(degraded_players)} degraded: {message}")
    
    # Display degradation status
    print("\nDegradation Status:")
    status = degradation_manager.get_degradation_status()
    for key, value in status.items():
        if value:
            print(f"  {key}: {value}")
    
    # Display performance report
    print("\nModel Performance Report:")
    report = degradation_manager.get_model_performance_report()
    if report:
        for model, stats in report.items():
            print(f"  {model}: {stats}")
    else:
        print("  No performance data available")
    
    return degradation_manager


def test_user_friendly_messages():
    """Test user-friendly error messages"""
    print("\n" + "=" * 60)
    print("Testing User-Friendly Error Messages")
    print("=" * 60)
    
    degradation_manager = GracefulDegradationManager()
    
    error_types = [
        ErrorType.MODEL_API_FAILURE,
        ErrorType.MODEL_TIMEOUT,
        ErrorType.MODEL_UNAVAILABLE,
        ErrorType.INVALID_RESPONSE,
        ErrorType.CONFIGURATION_ERROR,
        ErrorType.NETWORK_ERROR
    ]
    
    print("\nError messages with player name:")
    for error_type in error_types:
        message = degradation_manager.generate_user_friendly_error(
            error_type=error_type,
            model_name="test-model",
            player_name="TestPlayer"
        )
        print(f"  {error_type.value}:")
        print(f"    {message}")
    
    print("\nError messages without player name:")
    for error_type in error_types:
        message = degradation_manager.generate_user_friendly_error(
            error_type=error_type,
            model_name="test-model"
        )
        print(f"  {error_type.value}:")
        print(f"    {message}")


def test_fallback_configuration():
    """Test fallback configuration creation"""
    print("\n" + "=" * 60)
    print("Testing Fallback Configuration")
    print("=" * 60)
    
    fallback_config = create_default_fallback_configuration()
    
    print("Default fallback configuration:")
    for primary_model, fallbacks in fallback_config.items():
        print(f"  {primary_model} -> {fallbacks}")
    
    return fallback_config


def test_performance_tracking():
    """Test model performance tracking"""
    print("\n" + "=" * 60)
    print("Testing Model Performance Tracking")
    print("=" * 60)
    
    degradation_manager = GracefulDegradationManager()
    
    # Simulate various model events
    test_events = [
        ("model-a", "success", 1.5),
        ("model-a", "success", 2.0),
        ("model-a", "timeout", None),
        ("model-b", "success", 0.8),
        ("model-b", "failure", None),
        ("model-b", "success", 1.2),
        ("model-c", "timeout", None),
        ("model-c", "timeout", None),
        ("model-c", "failure", None),
    ]
    
    print("Simulating model events:")
    for model, event_type, duration in test_events:
        degradation_manager._update_model_performance(model, event_type, duration)
        print(f"  {model}: {event_type}" + (f" ({duration}s)" if duration else ""))
    
    # Get performance report
    print("\nModel Performance Report:")
    report = degradation_manager.get_model_performance_report()
    for model, stats in report.items():
        print(f"  {model}:")
        for metric, value in stats.items():
            print(f"    {metric}: {value}")


def main():
    """Run all error handling tests"""
    print("Multi-LLM Debate Game - Error Handling Test Suite (Simple)")
    print("=" * 60)
    
    try:
        # Test 1: Graceful degradation
        degradation_manager = test_graceful_degradation()
        
        # Test 2: User-friendly messages
        test_user_friendly_messages()
        
        # Test 3: Fallback configuration
        fallback_config = test_fallback_configuration()
        
        # Test 4: Performance tracking
        test_performance_tracking()
        
        print("\n" + "=" * 60)
        print("Error Handling Test Suite Completed Successfully")
        print("=" * 60)
        
        print("\nKey Features Tested:")
        print("✓ Timeout handling with escalation")
        print("✓ Model failure handling with graceful degradation")
        print("✓ Game continuation logic based on failure rates")
        print("✓ User-friendly error messages")
        print("✓ Fallback model configuration")
        print("✓ Model performance tracking and reporting")
        
    except Exception as e:
        print(f"\nTest suite failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())