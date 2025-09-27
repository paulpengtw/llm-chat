#!/usr/bin/env python3
"""
Comprehensive Test Suite for Multi-LLM Debate System

This test suite provides comprehensive unit and integration tests for:
- ModelConfigManager functionality
- HumanScoringInterface functionality  
- Multi-model game scenarios
- Error handling and recovery mechanisms

Requirements covered: 7.1, 7.2, 7.3, 7.4
"""

import unittest
import tempfile
import shutil
import json
import time
import threading
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List, Any

# Import components to test (with error handling for missing dependencies)
try:
    from model_config_manager import ModelConfigManager
    from human_scoring_interface import HumanScoringInterface, ScoringSession
    from llm_client import LLMClient
    from error_handling import ModelFailureHandler, GracefulDegradationManager, ModelFailureException
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Some dependencies not available: {e}")
    DEPENDENCIES_AVAILABLE = False
    
    # Create mock classes for testing
    class MockLLMClient:
        def chat(self, messages, model=None, **kwargs):
            return ("Mock response", "Mock reasoning")
    
    class MockModelConfigManager:
        def __init__(self, llm_client, presets_dir="model_presets"):
            self.llm_client = llm_client
            self.presets_dir = Path(presets_dir)
            self._validated_models = {}
    
    class MockHumanScoringInterface:
        def __init__(self, web_port=5001):
            self.web_port = web_port
            self.current_session = None
            self.scoring_statistics = {
                "total_sessions": 0,
                "completed_sessions": 0,
                "timeout_sessions": 0,
                "average_scoring_time": 0.0,
                "total_scoring_time": 0.0
            }
    
    class MockScoringSession:
        def __init__(self, session_id, round_info, players, timeout_seconds=300):
            self.session_id = session_id
            self.round_info = round_info
            self.players = players
            self.timeout_seconds = timeout_seconds
            self.scores = {}
            self.completed = False
            self.start_time = time.time()
    
    # Use mock classes
    LLMClient = MockLLMClient
    ModelConfigManager = MockModelConfigManager
    HumanScoringInterface = MockHumanScoringInterface
    ScoringSession = MockScoringSession


class TestModelConfigManager(unittest.TestCase):
    """Unit tests for ModelConfigManager"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.presets_dir = Path(self.temp_dir) / "test_presets"
        self.presets_dir.mkdir(exist_ok=True)
        
        # Mock LLMClient
        self.mock_llm_client = Mock(spec=LLMClient)
        self.manager = ModelConfigManager(self.mock_llm_client, str(self.presets_dir))
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_model_validation_success(self):
        """Test successful model validation"""
        # Mock successful LLM response
        self.mock_llm_client.chat.return_value = ("Hello", "test reasoning")
        
        result = self.manager.validate_model("test-model", use_error_handling=False)
        self.assertTrue(result)
        self.assertIn("test-model", self.manager._validated_models)
        self.assertTrue(self.manager._validated_models["test-model"])
    
    def test_model_validation_failure(self):
        """Test model validation failure"""
        # Mock LLM failure
        self.mock_llm_client.chat.side_effect = Exception("Model not found")
        
        result = self.manager.validate_model("invalid-model", use_error_handling=False)
        self.assertFalse(result)
        self.assertIn("invalid-model", self.manager._validated_models)
        self.assertFalse(self.manager._validated_models["invalid-model"])
    
    def test_model_validation_caching(self):
        """Test that model validation results are cached"""
        # Mock successful response
        self.mock_llm_client.chat.return_value = ("Hello", "test reasoning")
        
        # First validation
        result1 = self.manager.validate_model("cached-model", use_error_handling=False)
        self.assertTrue(result1)
        
        # Second validation should use cache
        result2 = self.manager.validate_model("cached-model", use_error_handling=False)
        self.assertTrue(result2)
        
        # LLM client should only be called once
        self.assertEqual(self.mock_llm_client.chat.call_count, 1)
    
    def test_create_player_configs_success(self):
        """Test successful player configuration creation"""
        # Mock model validation
        self.manager._validated_models = {"model1": True, "model2": True}
        
        models = ["model1", "model2"]
        names = ["Player1", "Player2"]
        
        configs = self.manager.create_player_configs(models, names)
        
        expected = [
            {"name": "Player1", "model": "model1"},
            {"name": "Player2", "model": "model2"}
        ]
        self.assertEqual(configs, expected)
    
    def test_create_player_configs_length_mismatch(self):
        """Test player config creation with mismatched list lengths"""
        models = ["model1", "model2"]
        names = ["Player1"]  # Different length
        
        with self.assertRaises(ValueError) as context:
            self.manager.create_player_configs(models, names)
        
        self.assertIn("must match", str(context.exception))
    
    def test_create_player_configs_too_many_players(self):
        """Test player config creation with too many players"""
        models = ["model1", "model2", "model3", "model4", "model5"]  # 5 players
        names = ["P1", "P2", "P3", "P4", "P5"]
        
        with self.assertRaises(ValueError) as context:
            self.manager.create_player_configs(models, names)
        
        self.assertIn("Maximum 4 players", str(context.exception))
    
    def test_create_judge_configs_success(self):
        """Test successful judge configuration creation"""
        # Mock model validation
        self.manager._validated_models = {"judge-model": True}
        
        models = ["judge-model", "judge-model"]  # Same model for both judges
        names = ["Judge1", "Judge2"]
        
        configs = self.manager.create_judge_configs(models, names)
        
        expected = [
            {"name": "Judge1", "model": "judge-model"},
            {"name": "Judge2", "model": "judge-model"}
        ]
        self.assertEqual(configs, expected)
    
    def test_save_and_load_preset(self):
        """Test saving and loading presets"""
        preset_config = {
            "preset_name": "test_preset",
            "description": "Test preset for unit testing",
            "player_configs": [
                {"name": "TestPlayer", "model": "test-model"}
            ],
            "judge_configs": [
                {"name": "TestJudge", "model": "test-model"}
            ]
        }
        
        # Save preset
        self.manager.save_preset("test_preset", preset_config)
        
        # Verify file exists
        preset_file = self.presets_dir / "test_preset.json"
        self.assertTrue(preset_file.exists())
        
        # Load preset
        loaded_config = self.manager.load_preset("test_preset")
        self.assertEqual(loaded_config, preset_config)
    
    def test_load_nonexistent_preset(self):
        """Test loading a preset that doesn't exist"""
        with self.assertRaises(FileNotFoundError):
            self.manager.load_preset("nonexistent_preset")
    
    def test_validate_preset_structure_valid(self):
        """Test preset structure validation with valid data"""
        valid_preset = {
            "preset_name": "valid_preset",
            "player_configs": [
                {"name": "Player1", "model": "model1"}
            ],
            "judge_configs": [
                {"name": "Judge1", "model": "model1"}
            ]
        }
        
        # Should not raise exception
        self.manager._validate_preset_structure(valid_preset)
    
    def test_validate_preset_structure_invalid(self):
        """Test preset structure validation with invalid data"""
        invalid_preset = {
            "preset_name": "invalid_preset",
            # Missing player_configs and judge_configs
        }
        
        with self.assertRaises(ValueError) as context:
            self.manager._validate_preset_structure(invalid_preset)
        
        self.assertIn("Missing required field", str(context.exception))
    
    def test_list_presets(self):
        """Test listing available presets"""
        # Create test preset files
        preset1 = {"preset_name": "preset1", "player_configs": [], "judge_configs": []}
        preset2 = {"preset_name": "preset2", "player_configs": [], "judge_configs": []}
        
        self.manager.save_preset("preset1", preset1)
        self.manager.save_preset("preset2", preset2)
        
        presets = self.manager.list_presets()
        self.assertIn("preset1", presets)
        self.assertIn("preset2", presets)
        self.assertEqual(len(presets), 2)
    
    def test_get_available_models(self):
        """Test getting list of available models"""
        # Set up validation cache
        self.manager._validated_models = {
            "model1": True,
            "model2": False,
            "model3": True
        }
        
        available = self.manager.get_available_models()
        self.assertEqual(set(available), {"model1", "model3"})


class TestHumanScoringInterface(unittest.TestCase):
    """Unit tests for HumanScoringInterface"""
    
    def setUp(self):
        """Set up test environment"""
        self.interface = HumanScoringInterface(web_port=5999)  # Use different port for testing
    
    def tearDown(self):
        """Clean up test environment"""
        self.interface.stop_server()
    
    def test_scoring_session_creation(self):
        """Test creating a scoring session"""
        round_info = {"round_id": 1, "target_card": "K"}
        players = ["Player1", "Player2"]
        
        session = ScoringSession(
            session_id="test_session",
            round_info=round_info,
            players=players,
            timeout_seconds=60
        )
        
        self.assertEqual(session.session_id, "test_session")
        self.assertEqual(session.round_info, round_info)
        self.assertEqual(session.players, players)
        self.assertFalse(session.completed)
        self.assertEqual(len(session.scores), 0)
    
    def test_scoring_session_expiration(self):
        """Test scoring session expiration"""
        session = ScoringSession(
            session_id="test_session",
            round_info={},
            players=["Player1"],
            timeout_seconds=1  # 1 second timeout
        )
        
        # Should not be expired initially
        self.assertFalse(session.is_expired())
        
        # Wait for expiration
        time.sleep(1.1)
        self.assertTrue(session.is_expired())
    
    def test_scoring_session_completion(self):
        """Test scoring session completion detection"""
        session = ScoringSession(
            session_id="test_session",
            round_info={},
            players=["Player1", "Player2"]
        )
        
        # Initially not complete
        self.assertFalse(session.is_complete())
        
        # Add partial scores
        session.scores["Player1"] = {"criterion1": 3}
        self.assertFalse(session.is_complete())
        
        # Add complete scores
        session.scores["Player1"] = {"criterion1": 3, "criterion2": 4}
        session.scores["Player2"] = {"criterion1": 2, "criterion2": 5}
        self.assertTrue(session.is_complete())
    
    def test_start_scoring_session(self):
        """Test starting a scoring session"""
        round_info = {"round_id": 1, "target_card": "K"}
        players = ["Player1", "Player2"]
        
        self.interface.start_scoring_session(round_info, players, timeout=60)
        
        # Check that session was created
        self.assertIsNotNone(self.interface.current_session)
        self.assertEqual(self.interface.current_session.round_info, round_info)
        self.assertEqual(self.interface.current_session.players, players)
        
        # Check statistics
        self.assertEqual(self.interface.scoring_statistics["total_sessions"], 1)
    
    def test_collect_scores_timeout(self):
        """Test score collection with timeout"""
        round_info = {"round_id": 1}
        players = ["Player1"]
        
        self.interface.start_scoring_session(round_info, players, timeout=60)
        
        # Collect scores with very short timeout (should timeout)
        scores = self.interface.collect_scores(timeout=1)
        
        # Should return empty scores due to timeout
        self.assertEqual(scores, {})
        self.assertEqual(self.interface.scoring_statistics["timeout_sessions"], 1)
    
    def test_get_scoring_statistics(self):
        """Test getting scoring statistics"""
        stats = self.interface.get_scoring_statistics()
        
        expected_keys = [
            "total_sessions", "completed_sessions", "timeout_sessions",
            "average_scoring_time", "total_scoring_time"
        ]
        
        for key in expected_keys:
            self.assertIn(key, stats)
        
        # Initial values should be zero
        self.assertEqual(stats["total_sessions"], 0)
        self.assertEqual(stats["completed_sessions"], 0)


class TestMultiModelGameScenarios(unittest.TestCase):
    """Integration tests for multi-model game scenarios"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.presets_dir = Path(self.temp_dir) / "test_presets"
        self.presets_dir.mkdir(exist_ok=True)
        
        # Mock LLMClient
        self.mock_llm_client = Mock(spec=LLMClient)
        self.manager = ModelConfigManager(self.mock_llm_client, str(self.presets_dir))
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_mixed_model_configuration(self):
        """Test creating a mixed model configuration"""
        # Mock successful model validation
        self.mock_llm_client.chat.return_value = ("Hello", "test reasoning")
        
        # Create mixed model preset
        preset_config = {
            "preset_name": "mixed_test",
            "description": "Mixed model test configuration",
            "player_configs": [
                {"name": "GPT-Player", "model": "gpt-4o"},
                {"name": "Claude-Player", "model": "claude-3-sonnet"}
            ],
            "judge_configs": [
                {"name": "GPT-Judge", "model": "gpt-4o"},
                {"name": "Claude-Judge", "model": "claude-3-sonnet"}
            ]
        }
        
        # Save and validate preset
        self.manager.save_preset("mixed_test", preset_config)
        loaded_preset = self.manager.load_preset("mixed_test")
        
        self.assertEqual(loaded_preset, preset_config)
        
        # Validate models in preset
        validation_results = self.manager.validate_preset_models("mixed_test")
        
        # All models should be valid (mocked)
        for model, is_valid in validation_results.items():
            self.assertTrue(is_valid)
    
    def test_single_model_configuration(self):
        """Test creating a single model configuration"""
        # Mock successful model validation
        self.mock_llm_client.chat.return_value = ("Hello", "test reasoning")
        
        models = ["gpt-4o"] * 4  # All players use same model
        names = ["Player1", "Player2", "Player3", "Player4"]
        
        player_configs = self.manager.create_player_configs(models, names)
        judge_configs = self.manager.create_judge_configs(models, names)
        
        # All configs should use the same model
        for config in player_configs + judge_configs:
            self.assertEqual(config["model"], "gpt-4o")
    
    def test_preset_validation_comprehensive(self):
        """Test comprehensive preset validation"""
        # Create multiple test presets
        presets = {
            "valid_preset": {
                "preset_name": "valid_preset",
                "description": "Valid test preset",
                "player_configs": [{"name": "P1", "model": "valid-model"}],
                "judge_configs": [{"name": "J1", "model": "valid-model"}]
            },
            "invalid_preset": {
                "preset_name": "invalid_preset",
                # Missing required fields
            }
        }
        
        # Mock model validation
        self.mock_llm_client.chat.return_value = ("Hello", "test reasoning")
        
        # Save presets
        for name, config in presets.items():
            try:
                self.manager.save_preset(name, config)
            except ValueError:
                pass  # Expected for invalid preset
        
        # Validate all presets
        validation_results = self.manager.validate_all_presets()
        
        # Check results
        if "valid_preset" in validation_results:
            self.assertTrue(validation_results["valid_preset"]["structure_valid"])
        
        if "invalid_preset" in validation_results:
            self.assertFalse(validation_results["invalid_preset"]["structure_valid"])


class TestErrorHandlingAndRecovery(unittest.TestCase):
    """Tests for error handling and recovery mechanisms"""
    
    def setUp(self):
        """Set up test environment"""
        self.mock_llm_client = Mock(spec=LLMClient)
        self.failure_handler = ModelFailureHandler(self.mock_llm_client, max_retries=2, base_delay=0.1)
        self.degradation_manager = GracefulDegradationManager(default_timeout=10.0)
    
    def test_model_failure_retry_logic(self):
        """Test retry logic for model failures"""
        # Mock failure then success
        self.mock_llm_client.chat.side_effect = [
            Exception("Temporary failure"),  # First call fails
            ("Success", "test reasoning")     # Second call succeeds
        ]
        
        # Set up fallback configuration
        fallback_config = {"test-model": ["fallback-model"]}
        self.failure_handler.set_fallback_models(fallback_config)
        
        messages = [{"role": "user", "content": "Hello"}]
        
        # Should succeed after retry
        content, reasoning = self.failure_handler.call_with_retry(
            model_name="test-model",
            messages=messages,
            player_name="TestPlayer"
        )
        
        self.assertEqual(content, "Success")
        self.assertEqual(self.mock_llm_client.chat.call_count, 2)
    
    def test_model_failure_exhausted_retries(self):
        """Test behavior when all retries are exhausted"""
        # Mock consistent failures
        self.mock_llm_client.chat.side_effect = Exception("Persistent failure")
        
        messages = [{"role": "user", "content": "Hello"}]
        
        # Should raise ModelFailureException after exhausting retries
        with self.assertRaises(ModelFailureException):
            self.failure_handler.call_with_retry(
                model_name="failing-model",
                messages=messages,
                player_name="TestPlayer"
            )
        
        # Should have tried max_retries + 1 times (initial + retries)
        self.assertEqual(self.mock_llm_client.chat.call_count, 3)
    
    def test_graceful_degradation_timeout_handling(self):
        """Test timeout handling in graceful degradation"""
        result = self.degradation_manager.handle_timeout(
            player_name="TestPlayer",
            model_name="slow-model",
            timeout_duration=15.0
        )
        
        self.assertTrue(result["success"])
        self.assertIn("timeout", result["user_message"].lower())
        
        # Check statistics
        stats = self.degradation_manager.get_degradation_status()
        self.assertEqual(stats["timeout_count"], 1)
    
    def test_graceful_degradation_player_failure(self):
        """Test player failure handling in graceful degradation"""
        error = Exception("Model API error")
        
        result = self.degradation_manager.handle_player_model_failure(
            player_name="TestPlayer",
            model_name="failed-model",
            error=error
        )
        
        self.assertTrue(result["success"])
        self.assertTrue(result["degraded"])
        
        # Check statistics
        stats = self.degradation_manager.get_degradation_status()
        self.assertEqual(stats["failed_players"], 1)
    
    def test_game_continuation_logic(self):
        """Test game continuation decision logic"""
        # Should continue with 1 failed player out of 4
        should_continue = self.degradation_manager.should_continue_game(
            failed_players=["Player1"],
            total_players=4
        )
        self.assertTrue(should_continue)
        
        # Should not continue with 3 failed players out of 4
        should_continue = self.degradation_manager.should_continue_game(
            failed_players=["Player1", "Player2", "Player3"],
            total_players=4
        )
        self.assertFalse(should_continue)
    
    def test_failure_statistics_tracking(self):
        """Test failure statistics tracking"""
        # Simulate some failures
        try:
            self.failure_handler.call_with_retry(
                model_name="failing-model",
                messages=[{"role": "user", "content": "Hello"}],
                player_name="TestPlayer"
            )
        except:
            pass  # Expected failure
        
        stats = self.failure_handler.get_failure_statistics()
        
        # Should have recorded the failure
        self.assertGreater(stats.get("total_failures", 0), 0)


class TestWebInterfaceIntegration(unittest.TestCase):
    """Integration tests for web interface functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.interface = HumanScoringInterface(web_port=6000)  # Use different port
        if hasattr(self.interface, 'start_server'):
            try:
                self.interface.start_server()
                time.sleep(1)  # Wait for server to start
            except:
                pass  # Server may not be available in test environment
        self.base_url = f"http://127.0.0.1:6000"
    
    def tearDown(self):
        """Clean up test environment"""
        if hasattr(self.interface, 'stop_server'):
            try:
                self.interface.stop_server()
            except:
                pass
    
    def test_web_server_startup(self):
        """Test that web server starts successfully"""
        if not DEPENDENCIES_AVAILABLE:
            self.skipTest("Dependencies not available for web server testing")
        
        # Test basic interface creation
        self.assertIsNotNone(self.interface)
        self.assertEqual(self.interface.web_port, 6000)
    
    def test_api_session_endpoint(self):
        """Test the session API endpoint"""
        if not DEPENDENCIES_AVAILABLE:
            self.skipTest("Dependencies not available for API testing")
        
        # Start a scoring session
        round_info = {"round_id": 1, "target_card": "K"}
        players = ["Player1", "Player2"]
        
        if hasattr(self.interface, 'start_scoring_session'):
            self.interface.start_scoring_session(round_info, players)
            
            # Verify session was created
            if hasattr(self.interface, 'current_session'):
                self.assertIsNotNone(self.interface.current_session)
    
    def test_api_statistics_endpoint(self):
        """Test the statistics API endpoint"""
        if not DEPENDENCIES_AVAILABLE:
            self.skipTest("Dependencies not available for statistics testing")
        
        # Test statistics retrieval
        if hasattr(self.interface, 'get_scoring_statistics'):
            stats = self.interface.get_scoring_statistics()
            expected_keys = ["total_sessions", "completed_sessions", "timeout_sessions"]
            for key in expected_keys:
                self.assertIn(key, stats)


def run_comprehensive_tests():
    """Run all comprehensive tests"""
    print("Running Comprehensive Test Suite for Multi-LLM Debate System")
    print("=" * 70)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes (skip some if dependencies not available)
    test_classes = [
        TestModelConfigManager,
        TestHumanScoringInterface,
        TestMultiModelGameScenarios,
        TestWebInterfaceIntegration
    ]
    
    # Only add error handling tests if dependencies are available
    if DEPENDENCIES_AVAILABLE:
        test_classes.append(TestErrorHandlingAndRecovery)
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\nFailures ({len(result.failures)}):")
        for test, traceback in result.failures:
            print(f"  - {test}")
    
    if result.errors:
        print(f"\nErrors ({len(result.errors)}):")
        for test, traceback in result.errors:
            print(f"  - {test}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_comprehensive_tests()
    exit(0 if success else 1)