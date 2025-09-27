"""
Simple Game Runner for Web Interface

This module provides a simple game runner that can be imported by the web interface.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

def run_game():
    """Run a simple game for web interface demonstration"""
    try:
        print("🎮 Starting Multi-LLM Debate Game")
        print("=" * 50)
        
        # Import game components
        from game import Game
        from llm_client import LLMClient
        from model_config_manager import ModelConfigManager
        
        # Initialize components
        llm_client = LLMClient()
        model_manager = ModelConfigManager(llm_client)
        
        # Create simple configuration
        player_configs = [
            {"name": "Alice", "model": "deepseek-r1"},
            {"name": "Bob", "model": "deepseek-r1"},
            {"name": "Charlie", "model": "deepseek-r1"},
            {"name": "Diana", "model": "deepseek-r1"}
        ]

        judge_configs = [
            {"name": "Justice", "model": "deepseek-r1"},
            {"name": "Wisdom", "model": "deepseek-r1"},
            {"name": "Truth", "model": "deepseek-r1"},
            {"name": "Honor", "model": "deepseek-r1"}
        ]
        
        print("Creating game with model validation...")
        
        # Create and start game
        game = Game(
            player_configs=player_configs,
            judge_configs=judge_configs,
            model_config_manager=model_manager,
            enable_human_scoring=False,
            enable_analytics=True
        )
        
        print("🚀 Game created successfully!")
        print("Starting game loop...")
        
        game.start_game()
        
        print("✅ Game completed!")
        
    except Exception as e:
        print(f"❌ Error running game: {e}")
        import traceback
        traceback.print_exc()

def run_enhanced_game():
    """Run enhanced game with web integration"""
    from enhanced_game_runner import run_enhanced_game as run_enhanced
    run_enhanced()

if __name__ == "__main__":
    run_game()