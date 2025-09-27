#!/usr/bin/env python3
"""
Test script for the error handling and recovery system.

This script tests various error scenarios to ensure the system handles
failures gracefully and provides appropriate fallback responses.
"""

import sys
import time
from typing import Dict, List
from llm_client import LLMClient
from error_handling import (
    ModelFailureHandler, 
    GracefulDegradationManager, 
    ModelFailureException,
    ErrorType,
    create_default_fallback_configuration
)
from model_config_manager import ModelConfigManager
from player import Player


def test_model_validation():
    """Test model validation with error handling"""
    print("=" * 60)
    print("Testing Model Validation with Error Handling")
    print("=" * 60)
    
    llm_client = LLMClient()
    manager = ModelConfigManager(llm_client)
    
    # Test valid and invalid models
    test_models = [
        "deepseek-r1",           # Should be valid
        "invalid-model-123",     # Should be invalid
        "openai/gpt-4o-mini",   # May be valid depending on configuration
    ]
    
    for model in test_models:
        print(f"\nTesting model: {model}")
        try:
            is_valid = manager.validate_model(model, use_error_handling=True)
            status = "✓ Valid" if is_valid else "✗ Invalid"
            print(f"  Result: {status}")
        except Exception as e:
            print(f"  Error: {e}")
    
    return manager


def test_failure_handler():
    """Test the failure handler with retry logic"""
    print("\n" + "=" * 60)
    print("Testing Failure Handler with Retry Logic")
    print("=" * 60)
    
    llm_client = LLMClient()
    failure_handler = ModelFailureHandler(llm_client, max_retries=2, base_delay=0.5)
    
    # Set up fallback configuration
    fallback_config = create_default_fallback_configuration()
    failure_handler.set_fallback_models(fallback_config)
    
    # Test with a valid model
    print("\nTesting with valid model:")
    try:
        messages = [{"role": "user", "content": "Say 'Hello World'"}]
        content, reasoning = failure_handler.call_with_retry(
            model_name="deepseek-r1",
            messages=messages,
            player_name="TestPlayer",
            timeout=30.0
        )
        print(f"✓ Success: {content[:50]}...")
    except Exception as e:
        print(f"✗ Failed: {e}")
    
    # Test with an invalid model (should trigger fallback)
    print("\nTesting with invalid model (should trigger fallback):")
    try:
        messages = [{"role": "user", "content": "Say 'Hello World'"}]
        content, reasoning = failure_handler.call_with_retry(
            model_name="invalid-model-name",
            messages=messages,
            player_name="TestPlayer",
            timeout=30.0
        )
        print(f"✓ Fallback success: {content[:50]}...")
    except ModelFailureException as e:
        print(f"✗ All fallbacks failed: {e}")
    
    # Display failure statistics
    print("\nFailure Statistics:")
    stats = failure_handler.get_failure_statistics()
    for key, value in stats.items():
        if value:
            print(f"  {key}: {value}")
    
    return failure_handler


def test_graceful_degradation():
    """Test graceful degradation manager"""
    print("\n" + "=" * 60)
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
    print(f"Timeout handled: {timeout_result['success']}")
    print(f"User message: {timeout_result.get('user_message', 'No message')}")
    
    # Test model failure handling
    print("\nTesting model failure handling:")
    failure_result = degradation_manager.handle_player_model_failure(
        player_name="TestPlayer",
        model_name="failed-model",
        error=Exception("Model API error")
    )
    print(f"Failure handled: {failure_result['success']}")
    print(f"Degraded: {failure_result['degraded']}")
    
    # Test game continuation logic
    print("\nTesting game continuation logic:")
    should_continue = degradation_manager.should_continue_game(
        failed_players=["Player1"], 
        total_players=4
    )
    print(f"Should continue with 1/4 failed: {should_continue}")
    
    should_continue = degradation_manager.should_continue_game(
        failed_players=["Player1", "Player2", "Player3"], 
        total_players=4
    )
    print(f"Should continue with 3/4 failed: {should_continue}")
    
    # Display degradation status
    print("\nDegradation Status:")
    status = degradation_manager.get_degradation_status()
    for key, value in status.items():
        if value:
            print(f"  {key}: {value}")
    
    # Display performance report
    print("\nModel Performance Report:")
    report = degradation_manager.get_model_performance_report()
    for model, stats in report.items():
        print(f"  {model}: {stats}")
    
    return degradation_manager


def test_player_error_handling():
    """Test player-level error handling"""
    print("\n" + "=" * 60)
    print("Testing Player Error Handling")
    print("=" * 60)
    
    # Create error handling components
    llm_client = LLMClient()
    failure_handler = ModelFailureHandler(llm_client, max_retries=1, base_delay=0.5)
    degradation_manager = GracefulDegradationManager(default_timeout=10.0)
    
    fallback_config = create_default_fallback_configuration()
    failure_handler.set_fallback_models(fallback_config)
    
    # Create a test player
    player = Player(
        name="TestPlayer",
        model_name="deepseek-r1",
        failure_handler=failure_handler,
        degradation_manager=degradation_manager
    )
    
    # Give the player some cards
    player.hand = ["K", "K", "Q"]
    
    print(f"\nTesting player {player.name} with model {player.model_name}")
    print(f"Player hand: {player.hand}")
    
    # Test choose_cards_to_play with error handling
    print("\nTesting choose_cards_to_play with error handling:")
    try:
        result, reasoning = player.choose_cards_to_play(
            round_base_info="Target card: K",
            round_action_info="No previous actions",
            play_decision_info="First player to act"
        )
        print(f"✓ Play decision successful:")
        print(f"  Played cards: {result['played_cards']}")
        print(f"  Behavior: {result['behavior']}")
        print(f"  Remaining hand: {player.hand}")
    except Exception as e:
        print(f"✗ Play decision failed: {e}")
    
    return player


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
    
    for error_type in error_types:
        message = degradation_manager.generate_user_friendly_error(
            error_type=error_type,
            model_name="test-model",
            player_name="TestPlayer"
        )
        print(f"\n{error_type.value}:")
        print(f"  {message}")


def main():
    """Run all error handling tests"""
    print("Multi-LLM Debate Game - Error Handling Test Suite")
    print("=" * 60)
    
    try:
        # Test 1: Model validation
        manager = test_model_validation()
        
        # Test 2: Failure handler
        failure_handler = test_failure_handler()
        
        # Test 3: Graceful degradation
        degradation_manager = test_graceful_degradation()
        
        # Test 4: Player error handling
        player = test_player_error_handling()
        
        # Test 5: User-friendly messages
        test_user_friendly_messages()
        
        print("\n" + "=" * 60)
        print("Error Handling Test Suite Completed")
        print("=" * 60)
        
        # Display final statistics
        print("\nFinal Error Statistics:")
        if manager:
            error_stats = manager.get_error_statistics()
            for category, stats in error_stats.items():
                if stats:
                    print(f"  {category}: {stats}")
        
    except Exception as e:
        print(f"\nTest suite failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())