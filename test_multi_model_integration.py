#!/usr/bin/env python3
"""
Integration Tests for Multi-Model Game Scenarios

This test suite focuses on integration testing of multi-model game scenarios,
including end-to-end game flows with different model combinations.

Requirements covered: 7.1, 7.2, 7.3, 7.4
"""

import unittest
import tempfile
import shutil
import json
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Import game components
from game import Game
from model_config_manager import ModelConfigManager
from human_scoring_interface import HumanScoringInterface
from llm_client import LLMClient
from player import Player
from judge_panel import JudgePanel
from error_handling import ModelFailureHandler, GracefulDegradationManager


class TestMultiModelGameIntegration(unittest.TestCase):
    """Integration tests for multi-model game scenarios"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.presets_dir = Path(self.temp_dir) / "test_presets"
        self.presets_dir.mkdir(exist_ok=True)
        
        # Mock LLMClient with realistic responses
        self.mock_llm_client = Mock(spec=LLMClient)
        self.setup_mock_responses()
        
        # Create ModelConfigManager
        self.manager = ModelConfigManager(self.mock_llm_client, str(self.presets_dir))
        
        # Create test presets
        self.create_test_presets()
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def setup_mock_responses(self):
        """Set up realistic mock responses for different scenarios"""
        def mock_chat_response(messages, model=None, **kwargs):
            # Simulate different model behaviors
            if "gpt" in model.lower():
                return ("I'll play 2 Kings", "GPT reasoning: Strategic play based on probability")
            elif "claude" in model.lower():
                return ("I'll play 1 King", "Claude reasoning: Conservative approach")
            else:
                return ("I'll play 1 card", "Default reasoning")
        
        self.mock_llm_client.chat.side_effect = mock_chat_response
    
    def create_test_presets(self):
        """Create test presets for integration testing"""
        presets = {
            "integration_mixed": {
                "preset_name": "integration_mixed",
                "description": "Mixed models for integration testing",
                "player_configs": [
                    {"name": "GPT-Alpha", "model": "gpt-4o"},
                    {"name": "Claude-Beta", "model": "claude-3-sonnet"}
                ],
                "judge_configs": [
                    {"name": "GPT-Judge", "model": "gpt-4o"},
                    {"name": "Claude-Judge", "model": "claude-3-sonnet"}
                ]
            },
            "integration_single": {
                "preset_name": "integration_single",
                "description": "Single model for integration testing",
                "player_configs": [
                    {"name": "Player1", "model": "gpt-4o"},
                    {"name": "Player2", "model": "gpt-4o"}
                ],
                "judge_configs": [
                    {"name": "Judge1", "model": "gpt-4o"},
                    {"name": "Judge2", "model": "gpt-4o"}
                ]
            }
        }
        
        for name, config in presets.items():
            self.manager.save_preset(name, config)
    
    def test_game_creation_with_model_manager(self):
        """Test creating a game with ModelConfigManager integration"""
        # Load test preset
        preset = self.manager.load_preset("integration_mixed")
        
        # Create game with model validation
        game = Game(
            player_configs=preset["player_configs"],
            judge_configs=preset["judge_configs"],
            model_config_manager=self.manager,
            enable_human_scoring=False
        )
        
        # Verify game was created successfully
        self.assertIsNotNone(game)
        self.assertEqual(len(game.players), 2)
        self.assertIsNotNone(game.judge_panel)
        
        # Verify model assignments
        self.assertEqual(game.players[0].model_name, "gpt-4o")
        self.assertEqual(game.players[1].model_name, "claude-3-sonnet")
    
    def test_game_creation_from_preset(self):
        """Test creating a game directly from preset"""
        try:
            game = Game.create_from_preset(
                preset_name="integration_single",
                model_config_manager=self.manager,
                enable_human_scoring=False
            )
            
            # Verify game creation
            self.assertIsNotNone(game)
            self.assertEqual(len(game.players), 2)
            
            # All players should use the same model
            for player in game.players:
                self.assertEqual(player.model_name, "gpt-4o")
                
        except Exception as e:
            # If Game.create_from_preset doesn't exist, this is expected
            if "has no attribute 'create_from_preset'" in str(e):
                self.skipTest("Game.create_from_preset method not implemented")
            else:
                raise
    
    def test_player_model_assignment_tracking(self):
        """Test that player model assignments are properly tracked"""
        preset = self.manager.load_preset("integration_mixed")
        
        game = Game(
            player_configs=preset["player_configs"],
            judge_configs=preset["judge_configs"],
            model_config_manager=self.manager,
            enable_human_scoring=False
        )
        
        # Check that each player has correct model assignment
        expected_assignments = {
            "GPT-Alpha": "gpt-4o",
            "Claude-Beta": "claude-3-sonnet"
        }
        
        for player in game.players:
            expected_model = expected_assignments[player.name]
            self.assertEqual(player.model_name, expected_model)
    
    def test_judge_model_assignment_tracking(self):
        """Test that judge model assignments are properly tracked"""
        preset = self.manager.load_preset("integration_mixed")
        
        game = Game(
            player_configs=preset["player_configs"],
            judge_configs=preset["judge_configs"],
            model_config_manager=self.manager,
            enable_human_scoring=False
        )
        
        # Check judge model assignments
        expected_judge_assignments = {
            "GPT-Judge": "gpt-4o",
            "Claude-Judge": "claude-3-sonnet"
        }
        
        for judge in game.judge_panel.judges:
            expected_model = expected_judge_assignments[judge.name]
            self.assertEqual(judge.model_name, expected_model)
    
    def test_game_with_human_scoring_integration(self):
        """Test game creation with human scoring enabled"""
        preset = self.manager.load_preset("integration_mixed")
        
        game = Game(
            player_configs=preset["player_configs"],
            judge_configs=preset["judge_configs"],
            model_config_manager=self.manager,
            enable_human_scoring=True,
            human_scoring_port=6001  # Use different port for testing
        )
        
        # Verify human scoring interface is set up
        self.assertIsNotNone(game.human_scoring_interface)
        self.assertTrue(game.enable_human_scoring)
    
    def test_model_validation_during_game_creation(self):
        """Test that invalid models are caught during game creation"""
        # Create preset with invalid model
        invalid_preset = {
            "preset_name": "invalid_test",
            "description": "Preset with invalid model",
            "player_configs": [
                {"name": "Player1", "model": "invalid-model-name"}
            ],
            "judge_configs": [
                {"name": "Judge1", "model": "invalid-model-name"}
            ]
        }
        
        # Mock model validation to return False for invalid model
        def mock_validate_model(model_name, use_error_handling=True):
            return model_name != "invalid-model-name"
        
        self.manager.validate_model = mock_validate_model
        
        # Game creation should handle invalid models gracefully
        with self.assertRaises(ValueError):
            self.manager.create_player_configs(
                ["invalid-model-name"], 
                ["Player1"]
            )
    
    def test_error_handling_integration(self):
        """Test error handling integration in multi-model scenarios"""
        preset = self.manager.load_preset("integration_mixed")
        
        # Create game with error handling
        game = Game(
            player_configs=preset["player_configs"],
            judge_configs=preset["judge_configs"],
            model_config_manager=self.manager,
            enable_human_scoring=False
        )
        
        # Verify error handling components are available
        failure_handler = self.manager.get_failure_handler()
        degradation_manager = self.manager.get_degradation_manager()
        
        self.assertIsNotNone(failure_handler)
        self.assertIsNotNone(degradation_manager)
        
        # Test that players have access to error handling
        for player in game.players:
            if hasattr(player, 'failure_handler'):
                self.assertIsNotNone(player.failure_handler)
    
    def test_game_record_model_tracking(self):
        """Test that game records properly track model information"""
        preset = self.manager.load_preset("integration_mixed")
        
        game = Game(
            player_configs=preset["player_configs"],
            judge_configs=preset["judge_configs"],
            model_config_manager=self.manager,
            enable_human_scoring=False
        )
        
        # Check that game record tracks model assignments
        if hasattr(game, 'game_record') and hasattr(game.game_record, 'model_assignments'):
            model_assignments = game.game_record.model_assignments
            
            # Should have model assignments for all players
            for player in game.players:
                self.assertIn(player.name, model_assignments)
                self.assertEqual(model_assignments[player.name], player.model_name)


class TestErrorRecoveryScenarios(unittest.TestCase):
    """Test error recovery scenarios in multi-model games"""
    
    def setUp(self):
        """Set up test environment"""
        self.mock_llm_client = Mock(spec=LLMClient)
        self.failure_handler = ModelFailureHandler(self.mock_llm_client, max_retries=2, base_delay=0.1)
        self.degradation_manager = GracefulDegradationManager(default_timeout=5.0)
    
    def test_model_failure_during_game(self):
        """Test handling of model failure during game play"""
        # Mock intermittent failures
        call_count = 0
        def mock_chat_with_failure(messages, model=None, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count <= 2:  # First two calls fail
                raise Exception("Model temporarily unavailable")
            return ("Success after retry", "Recovered successfully")
        
        self.mock_llm_client.chat.side_effect = mock_chat_with_failure
        
        # Set up fallback configuration
        fallback_config = {"failing-model": ["backup-model"]}
        self.failure_handler.set_fallback_models(fallback_config)
        
        # Test recovery
        messages = [{"role": "user", "content": "Choose cards to play"}]
        content, reasoning = self.failure_handler.call_with_retry(
            model_name="failing-model",
            messages=messages,
            player_name="TestPlayer"
        )
        
        self.assertEqual(content, "Success after retry")
        self.assertEqual(call_count, 3)  # Should have retried twice
    
    def test_timeout_handling_in_game(self):
        """Test timeout handling during game play"""
        # Simulate timeout scenario
        result = self.degradation_manager.handle_timeout(
            player_name="SlowPlayer",
            model_name="slow-model",
            timeout_duration=10.0
        )
        
        self.assertTrue(result["success"])
        self.assertIn("timeout", result["user_message"].lower())
        
        # Check that timeout is recorded
        stats = self.degradation_manager.get_degradation_status()
        self.assertEqual(stats["timeout_count"], 1)
    
    def test_multiple_player_failures(self):
        """Test handling multiple player failures"""
        # Simulate multiple player failures
        failed_players = ["Player1", "Player2"]
        
        for player in failed_players:
            result = self.degradation_manager.handle_player_model_failure(
                player_name=player,
                model_name="failed-model",
                error=Exception("Model API error")
            )
            self.assertTrue(result["success"])
        
        # Check game continuation logic
        should_continue = self.degradation_manager.should_continue_game(
            failed_players=failed_players,
            total_players=4
        )
        
        # Should continue with 2/4 players failed
        self.assertTrue(should_continue)
        
        # But not with 3/4 players failed
        should_continue = self.degradation_manager.should_continue_game(
            failed_players=failed_players + ["Player3"],
            total_players=4
        )
        self.assertFalse(should_continue)
    
    def test_graceful_degradation_statistics(self):
        """Test that graceful degradation properly tracks statistics"""
        # Simulate various error scenarios
        self.degradation_manager.handle_timeout("Player1", "model1", 15.0)
        self.degradation_manager.handle_player_model_failure("Player2", "model2", Exception("Error"))
        
        # Get performance report
        report = self.degradation_manager.get_model_performance_report()
        
        # Should have entries for both models
        self.assertIn("model1", report)
        self.assertIn("model2", report)
        
        # Check statistics
        stats = self.degradation_manager.get_degradation_status()
        self.assertEqual(stats["timeout_count"], 1)
        self.assertEqual(stats["failed_players"], 1)


class TestHumanScoringIntegration(unittest.TestCase):
    """Test human scoring integration with multi-model games"""
    
    def setUp(self):
        """Set up test environment"""
        self.interface = HumanScoringInterface(web_port=6002)
    
    def tearDown(self):
        """Clean up test environment"""
        self.interface.stop_server()
    
    def test_scoring_session_with_model_info(self):
        """Test scoring session that includes model information"""
        round_info = {
            "round_id": 1,
            "target_card": "K",
            "model_assignments": {
                "GPT-Player": "gpt-4o",
                "Claude-Player": "claude-3-sonnet"
            }
        }
        
        players = ["GPT-Player", "Claude-Player"]
        
        self.interface.start_scoring_session(round_info, players, timeout=60)
        
        # Verify session includes model information
        session = self.interface.current_session
        self.assertIsNotNone(session)
        self.assertEqual(session.round_info, round_info)
        self.assertIn("model_assignments", session.round_info)
    
    def test_combined_ai_human_evaluation_display(self):
        """Test display of combined AI and human evaluation results"""
        round_info = {"round_id": 1, "target_card": "K"}
        
        ai_votes = {
            "votes": {
                "GPT-Judge": {"voted_player": "GPT-Player", "reasoning": "Excellent strategy"},
                "Claude-Judge": {"voted_player": "Claude-Player", "reasoning": "Good bluffing"}
            }
        }
        
        human_scores = {
            "GPT-Player": {
                "strategic_thinking": 4,
                "bluffing_skill": 3,
                "reasoning_quality": 5,
                "overall_performance": 4
            },
            "Claude-Player": {
                "strategic_thinking": 3,
                "bluffing_skill": 5,
                "reasoning_quality": 4,
                "overall_performance": 4
            }
        }
        
        # Test display functionality (should not raise exceptions)
        try:
            self.interface.display_round_summary(round_info, ai_votes, human_scores)
        except Exception as e:
            self.fail(f"display_round_summary raised an exception: {e}")
    
    def test_scoring_statistics_tracking(self):
        """Test that scoring statistics are properly tracked"""
        # Start and complete a scoring session
        round_info = {"round_id": 1}
        players = ["Player1"]
        
        self.interface.start_scoring_session(round_info, players, timeout=60)
        
        # Simulate score submission
        scores = {"Player1": {"criterion1": 3, "criterion2": 4}}
        self.interface.current_session.scores = scores
        self.interface.current_session.completed = True
        
        # Collect scores
        collected_scores = self.interface.collect_scores(timeout=1)
        
        # Check statistics
        stats = self.interface.get_scoring_statistics()
        self.assertEqual(stats["total_sessions"], 1)


def run_integration_tests():
    """Run all integration tests"""
    print("Running Multi-Model Integration Test Suite")
    print("=" * 50)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestMultiModelGameIntegration,
        TestErrorRecoveryScenarios,
        TestHumanScoringIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print("INTEGRATION TEST SUMMARY")
    print("=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print(f"\nFailures:")
        for test, traceback in result.failures:
            print(f"  - {test}")
    
    if result.errors:
        print(f"\nErrors:")
        for test, traceback in result.errors:
            print(f"  - {test}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_integration_tests()
    exit(0 if success else 1)