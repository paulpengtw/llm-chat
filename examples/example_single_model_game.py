#!/usr/bin/env python3
"""
Example: Single Model Game

This example demonstrates how to run a game where all players and judges
use the same LLM model. This is useful for baseline testing and ensuring
consistent behavior across all participants.

Requirements covered: 3.1, 3.2, 1.3
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game import Game
from model_config_manager import ModelConfigManager
from llm_client import LLMClient


def run_single_model_game():
    """Run a game with a single model for all players and judges"""
    print("=" * 60)
    print("Single Model Game Example")
    print("=" * 60)
    print("This example runs a game where all players and judges use the same model.")
    print("This is useful for baseline testing and consistent behavior analysis.")
    print()
    
    try:
        # Initialize LLM client and model manager
        print("🔧 Initializing components...")
        llm_client = LLMClient()
        model_manager = ModelConfigManager(llm_client)
        
        # Define the model to use for all participants
        model_name = "deepseek-r1"  # Change this to your preferred model
        
        print(f"🤖 Using model: {model_name}")
        print("🔍 Validating model availability...")
        
        # Validate the model
        if not model_manager.validate_model(model_name):
            print(f"❌ Model '{model_name}' is not available.")
            print("Please check your model configuration or try a different model.")
            return False
        
        print("✅ Model validation successful!")
        
        # Create player configurations (all using the same model)
        print("👥 Creating player configurations...")
        player_models = [model_name] * 4
        player_names = ["Alpha", "Beta", "Gamma", "Delta"]
        
        player_configs = model_manager.create_player_configs(player_models, player_names)
        
        # Create judge configurations (all using the same model)
        print("⚖️  Creating judge configurations...")
        judge_models = [model_name] * 4
        judge_names = ["Justice", "Wisdom", "Truth", "Honor"]
        
        judge_configs = model_manager.create_judge_configs(judge_models, judge_names)
        
        # Display configuration
        print("\n📋 Game Configuration:")
        print("Players:")
        for config in player_configs:
            print(f"  • {config['name']}: {config['model']}")
        
        print("Judges:")
        for config in judge_configs:
            print(f"  • {config['name']}: {config['model']}")
        
        # Create and start the game
        print("\n🎮 Creating game...")
        game = Game(
            player_configs=player_configs,
            judge_configs=judge_configs,
            model_config_manager=model_manager,
            enable_human_scoring=False  # Disable for this example
        )
        
        print("✅ Game created successfully!")
        print("\n🚀 Starting game...")
        print("Note: This is a demonstration. In a real scenario, you would call game.play() here.")
        
        # Display game information
        print(f"\n📊 Game Information:")
        print(f"  Players: {len(game.players)}")
        print(f"  Judges: {len(game.judge_panel.judges)}")
        print(f"  Model: {model_name} (used by all participants)")
        
        # Show player status
        print("\n👥 Player Status:")
        for player in game.players:
            print(f"  {player.name}: Ready (Model: {player.model_name})")
        
        print("\n🎯 Single model game setup completed successfully!")
        print("All players and judges are using the same model for consistent behavior.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up single model game: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def create_single_model_preset():
    """Create and save a preset for single model games"""
    print("\n" + "=" * 60)
    print("Creating Single Model Preset")
    print("=" * 60)
    
    try:
        llm_client = LLMClient()
        model_manager = ModelConfigManager(llm_client)
        
        # Define preset configuration
        preset_config = {
            "preset_name": "single_model_baseline",
            "description": "Baseline configuration with all participants using the same model",
            "player_configs": [
                {"name": "Alpha", "model": "deepseek-r1"},
                {"name": "Beta", "model": "deepseek-r1"},
                {"name": "Gamma", "model": "deepseek-r1"},
                {"name": "Delta", "model": "deepseek-r1"}
            ],
            "judge_configs": [
                {"name": "Justice", "model": "deepseek-r1"},
                {"name": "Wisdom", "model": "deepseek-r1"},
                {"name": "Truth", "model": "deepseek-r1"},
                {"name": "Honor", "model": "deepseek-r1"}
            ]
        }
        
        # Save the preset
        model_manager.save_preset("single_model_baseline", preset_config)
        print("✅ Created preset: single_model_baseline")
        
        # Demonstrate loading the preset
        loaded_preset = model_manager.load_preset("single_model_baseline")
        print(f"✅ Verified preset loading: {loaded_preset['preset_name']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating preset: {str(e)}")
        return False


def demonstrate_preset_usage():
    """Demonstrate how to use presets for single model games"""
    print("\n" + "=" * 60)
    print("Preset Usage Demonstration")
    print("=" * 60)
    
    try:
        llm_client = LLMClient()
        model_manager = ModelConfigManager(llm_client)
        
        # List available presets
        presets = model_manager.list_presets()
        print(f"📋 Available presets: {', '.join(presets)}")
        
        # Load a single model preset
        if "single_model_test" in presets:
            preset = model_manager.load_preset("single_model_test")
            print(f"\n📖 Loaded preset: {preset['preset_name']}")
            print(f"Description: {preset['description']}")
            
            # Validate all models in the preset
            validation_results = model_manager.validate_preset_models("single_model_test")
            print(f"\n🔍 Model validation results:")
            for model, is_valid in validation_results.items():
                status = "✅ Valid" if is_valid else "❌ Invalid"
                print(f"  {model}: {status}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error demonstrating preset usage: {str(e)}")
        return False


def main():
    """Main function to run all single model examples"""
    print("Single Model Game Examples")
    print("This script demonstrates various aspects of single model games.")
    print()
    
    success = True
    
    # Run single model game example
    if not run_single_model_game():
        success = False
    
    # Create preset example
    if not create_single_model_preset():
        success = False
    
    # Demonstrate preset usage
    if not demonstrate_preset_usage():
        success = False
    
    if success:
        print("\n🎉 All single model examples completed successfully!")
        print("\nKey takeaways:")
        print("• Single model games provide consistent baseline behavior")
        print("• All participants use the same model for fair comparison")
        print("• Presets make it easy to reproduce configurations")
        print("• Model validation ensures reliability before game start")
    else:
        print("\n⚠️  Some examples encountered errors. Check the output above.")
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)