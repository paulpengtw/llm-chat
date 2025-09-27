"""
Enhanced Game Runner with Web Interface Integration

This module runs multi-LLM debate games with enhanced web interface integration,
providing real-time model performance indicators and analytics.
"""

import sys
import os
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from game import Game
from llm_client import LLMClient
from model_config_manager import ModelConfigManager
from game_analytics_integration import GameAnalyticsManager
from enhanced_main import update_game_state_from_game


def run_enhanced_game():
    """Run an enhanced multi-LLM debate game with web interface integration"""
    try:
        print("🚀 Starting Enhanced Multi-LLM Debate Game")
        print("=" * 60)
        
        # Initialize LLM client and model config manager
        llm_client = LLMClient()
        model_manager = ModelConfigManager(llm_client)
        
        # Try to use a preset configuration
        available_presets = model_manager.list_presets()
        print(f"Available presets: {available_presets}")
        
        # Select a preset or create a default configuration
        if "mixed_models_example" in available_presets:
            preset_name = "mixed_models_example"
            print(f"Using preset: {preset_name}")
            
            try:
                # Create game from preset
                game = Game.create_from_preset(
                    preset_name=preset_name,
                    model_config_manager=model_manager,
                    enable_human_scoring=False,  # Disable for web demo
                    enable_analytics=True
                )
                
            except Exception as e:
                print(f"Failed to create game from preset: {e}")
                print("Falling back to default configuration...")
                game = create_default_game(model_manager)
                
        else:
            print("No suitable preset found, using default configuration...")
            game = create_default_game(model_manager)
        
        # Set up web interface integration
        setup_web_integration(game)
        
        print("\n" + "=" * 60)
        print("🎮 Starting Enhanced Multi-LLM Debate Game!")
        print("🌐 Web interface available at: http://127.0.0.1:5000")
        print("=" * 60)
        
        # Start the game
        game.start_game()
        
        print("\n" + "=" * 60)
        print("🏁 Game completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error running enhanced game: {e}")
        import traceback
        traceback.print_exc()

def create_default_game(model_manager: ModelConfigManager) -> Game:
    """Create a default game configuration"""
    print("Creating default game configuration...")
    
    # Default configuration with available models
    player_configs = [
        {"name": "Alpha", "model": "deepseek-r1"},
        {"name": "Beta", "model": "deepseek-r1"},
        {"name": "Gamma", "model": "deepseek-r1"},
        {"name": "Delta", "model": "deepseek-r1"}
    ]

    judge_configs = [
        {"name": "Justice", "model": "deepseek-r1"},
        {"name": "Wisdom", "model": "deepseek-r1"},
        {"name": "Truth", "model": "deepseek-r1"},
        {"name": "Honor", "model": "deepseek-r1"}
    ]
    
    # Validate models
    print("Validating model configurations...")
    for config in player_configs + judge_configs:
        if not model_manager.validate_model(config["model"]):
            print(f"⚠️  Model '{config['model']}' validation failed, but continuing...")
    
    return Game(
        player_configs=player_configs,
        judge_configs=judge_configs,
        model_config_manager=model_manager,
        enable_human_scoring=False,
        enable_analytics=True
    )

def setup_web_integration(game: Game):
    """Set up web interface integration for the game"""
    print("Setting up web interface integration...")
    
    # Create a custom analytics manager that updates the web interface
    class WebIntegratedAnalyticsManager(GameAnalyticsManager):
        def update_session_progress(self, game_record):
            super().update_session_progress(game_record)
            # Update web interface with current game state
            update_game_state_from_game(game_record, self)
    
    # Replace the game's analytics manager with our web-integrated version
    if game.analytics_manager:
        web_analytics = WebIntegratedAnalyticsManager(game.analytics_manager.analytics)
        game.analytics_manager = web_analytics
    
    # Hook into game events to update web interface
    original_start_round_record = game.start_round_record
    original_reset_round = game.reset_round
    original_finish_game = game.game_record.finish_game
    
    def enhanced_start_round_record():
        original_start_round_record()
        update_game_state_from_game(game.game_record, game.analytics_manager)
    
    def enhanced_reset_round(use_current_player):
        original_reset_round(use_current_player)
        update_game_state_from_game(game.game_record, game.analytics_manager)
    
    def enhanced_finish_game(winner_name):
        original_finish_game(winner_name)
        update_game_state_from_game(game.game_record, game.analytics_manager)
    
    # Replace methods with enhanced versions
    game.start_round_record = enhanced_start_round_record
    game.reset_round = enhanced_reset_round
    game.game_record.finish_game = enhanced_finish_game
    
    # Initial state update
    update_game_state_from_game(game.game_record, game.analytics_manager)
    
    print("✅ Web interface integration configured")

def run_demo_game():
    """Run a demo game for testing the web interface"""
    print("🎬 Running Demo Game for Web Interface Testing")
    print("=" * 60)
    
    # Simulate game events for testing
    from enhanced_main import messages
    
    demo_messages = [
        "🎮 Demo Game Started",
        "Player Alpha (gpt-4o) is thinking...",
        "Alpha played 2 cards: K, K",
        "Player Beta (claude-3-sonnet) is deciding whether to challenge...",
        "Beta chose not to challenge",
        "Judge Justice (gpt-4o) is evaluating the round...",
        "⚖️ Judge votes: Alpha wins this round",
        "📊 Round 1 completed",
        "🏆 Game completed! Winner: Alpha"
    ]
    
    for i, message in enumerate(demo_messages):
        time.sleep(2)  # Simulate real-time game progression
        messages.put(f"[Demo {i+1}/9] {message}")
        print(f"Sent: {message}")
    
    print("Demo completed!")

if __name__ == "__main__":
    # Check if we should run demo mode
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        run_demo_game()
    else:
        run_enhanced_game()