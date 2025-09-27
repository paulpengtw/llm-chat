#!/usr/bin/env python3
"""
Example script demonstrating Multi-LLM Debate Game with ModelConfigManager integration.

This example shows how to:
1. Use ModelConfigManager for model validation
2. Create games from presets
3. Enable human scoring
4. Handle model configuration errors gracefully
"""

from game import Game
from model_config_manager import ModelConfigManager, create_default_presets
from llm_client import LLMClient

def main():
    """Main example demonstrating the new multi-LLM functionality"""
    print("Multi-LLM Debate Game Example")
    print("=" * 50)
    
    # Initialize the model configuration system
    print("1. Initializing ModelConfigManager...")
    llm_client = LLMClient()
    model_manager = ModelConfigManager(llm_client)
    
    # Create default presets if they don't exist
    print("2. Setting up default presets...")
    create_default_presets(model_manager)
    
    # List available presets
    available_presets = model_manager.list_presets()
    print(f"Available presets: {available_presets}")
    
    # Example 1: Create game from preset
    print("\n" + "=" * 50)
    print("EXAMPLE 1: Creating game from preset")
    print("=" * 50)
    
    try:
        if "single_model_test" in available_presets:
            print("Creating game from 'single_model_test' preset...")
            game1 = Game.create_from_preset(
                preset_name="single_model_test",
                model_config_manager=model_manager,
                enable_human_scoring=False
            )
            print("✓ Game created successfully from preset!")
            
            # You can start the game with: game1.start_game()
            print("Game ready to start. Call game1.start_game() to begin.")
        else:
            print("⚠ single_model_test preset not found")
    except Exception as e:
        print(f"❌ Error creating game from preset: {e}")
    
    # Example 2: Create game with custom configuration and human scoring
    print("\n" + "=" * 50)
    print("EXAMPLE 2: Custom configuration with human scoring")
    print("=" * 50)
    
    try:
        # Define custom player and judge configurations
        custom_player_configs = [
            {"name": "GPT-Alpha", "model": "openai/gpt-4o-mini"},
            {"name": "GPT-Beta", "model": "openai/gpt-4o-mini"},
            {"name": "GPT-Gamma", "model": "openai/gpt-4o-mini"},
            {"name": "GPT-Delta", "model": "openai/gpt-4o-mini"}
        ]
        
        custom_judge_configs = [
            {"name": "Justice", "model": "openai/gpt-4o-mini"},
            {"name": "Wisdom", "model": "openai/gpt-4o-mini"},
            {"name": "Truth", "model": "openai/gpt-4o-mini"},
            {"name": "Honor", "model": "openai/gpt-4o-mini"}
        ]
        
        print("Creating game with custom configuration and human scoring...")
        game2 = Game(
            player_configs=custom_player_configs,
            judge_configs=custom_judge_configs,
            model_config_manager=model_manager,  # This enables model validation
            enable_human_scoring=True,           # Enable human scoring
            human_scoring_port=5001             # Web interface port
        )
        print("✓ Game created with human scoring enabled!")
        print("Human scoring interface will be available at: http://127.0.0.1:5001")
        
        # You can start the game with: game2.start_game()
        print("Game ready to start. Call game2.start_game() to begin.")
        
    except Exception as e:
        print(f"❌ Error creating custom game: {e}")
    
    # Example 3: Demonstrate error handling for invalid models
    print("\n" + "=" * 50)
    print("EXAMPLE 3: Error handling for invalid models")
    print("=" * 50)
    
    try:
        invalid_configs = [
            {"name": "TestPlayer", "model": "invalid-model-name"}
        ]
        invalid_judge_configs = [
            {"name": "TestJudge", "model": "another-invalid-model"}
        ]
        
        print("Attempting to create game with invalid models...")
        game3 = Game(
            player_configs=invalid_configs,
            judge_configs=invalid_judge_configs,
            model_config_manager=model_manager  # This will catch invalid models
        )
        print("⚠ This should not print - invalid models should be caught")
        
    except ValueError as e:
        print(f"✓ Successfully caught invalid model configuration: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    
    # Example 4: Backward compatibility (no ModelConfigManager)
    print("\n" + "=" * 50)
    print("EXAMPLE 4: Backward compatibility")
    print("=" * 50)
    
    try:
        print("Creating game without ModelConfigManager (backward compatible)...")
        simple_configs = [
            {"name": "SimplePlayer", "model": "openai/gpt-4o-mini"}
        ]
        simple_judge_configs = [
            {"name": "SimpleJudge", "model": "openai/gpt-4o-mini"}
        ]
        
        game4 = Game(
            player_configs=simple_configs,
            judge_configs=simple_judge_configs
            # No model_config_manager - should work for backward compatibility
        )
        print("✓ Game created without ModelConfigManager (backward compatible)")
        
    except Exception as e:
        print(f"❌ Backward compatibility error: {e}")
    
    print("\n" + "=" * 50)
    print("EXAMPLE COMPLETE")
    print("=" * 50)
    print("Key features demonstrated:")
    print("  ✓ ModelConfigManager integration")
    print("  ✓ Preset-based game creation")
    print("  ✓ Human scoring integration")
    print("  ✓ Model validation and error handling")
    print("  ✓ Backward compatibility")
    print("\nTo actually run a game, uncomment the game.start_game() calls above.")

if __name__ == "__main__":
    main()