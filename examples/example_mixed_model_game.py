#!/usr/bin/env python3
"""
Example: Mixed Model Game

This example demonstrates how to run a game with different LLM models
competing against each other. This allows for comparative analysis of
different AI approaches to strategic gameplay.

Requirements covered: 3.1, 3.2, 1.3
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game import Game
from model_config_manager import ModelConfigManager
from llm_client import LLMClient


def run_mixed_model_game():
    """Run a game with different models for players and judges"""
    print("=" * 60)
    print("Mixed Model Game Example")
    print("=" * 60)
    print("This example runs a game with different LLM models competing.")
    print("This allows for comparative analysis of different AI approaches.")
    print()
    
    try:
        # Initialize LLM client and model manager
        print("🔧 Initializing components...")
        llm_client = LLMClient()
        model_manager = ModelConfigManager(llm_client)
        
        # Define different models for players
        player_models = [
            "deepseek-r1",           # Player 1: DeepSeek R1
            "openai/gpt-4o-mini",    # Player 2: GPT-4o Mini
            "anthropic/claude-3-5-sonnet",  # Player 3: Claude 3.5 Sonnet
            "deepseek-r1"            # Player 4: DeepSeek R1 (for comparison)
        ]
        
        player_names = ["DeepSeek-Alpha", "GPT-Mini", "Claude-Sonnet", "DeepSeek-Beta"]
        
        # Define different models for judges
        judge_models = [
            "deepseek-r1",           # Judge 1: DeepSeek R1
            "openai/gpt-4o-mini",    # Judge 2: GPT-4o Mini
            "anthropic/claude-3-5-sonnet",  # Judge 3: Claude 3.5 Sonnet
            "deepseek-r1"            # Judge 4: DeepSeek R1
        ]
        
        judge_names = ["DeepSeek-Justice", "GPT-Wisdom", "Claude-Truth", "DeepSeek-Honor"]
        
        print("🔍 Validating all models...")
        
        # Validate all unique models
        all_models = set(player_models + judge_models)
        invalid_models = []
        
        for model in all_models:
            print(f"  Checking {model}...")
            if not model_manager.validate_model(model):
                invalid_models.append(model)
        
        if invalid_models:
            print(f"❌ Invalid models found: {', '.join(invalid_models)}")
            print("Please update the model names or check your configuration.")
            print("\nAvailable models might include:")
            print("  • deepseek-r1")
            print("  • openai/gpt-4o")
            print("  • openai/gpt-4o-mini")
            print("  • anthropic/claude-3-5-sonnet")
            return False
        
        print("✅ All models validated successfully!")
        
        # Create player configurations
        print("👥 Creating player configurations...")
        player_configs = model_manager.create_player_configs(player_models, player_names)
        
        # Create judge configurations
        print("⚖️  Creating judge configurations...")
        judge_configs = model_manager.create_judge_configs(judge_models, judge_names)
        
        # Display configuration
        print("\n📋 Mixed Model Game Configuration:")
        print("Players:")
        for config in player_configs:
            print(f"  • {config['name']}: {config['model']}")
        
        print("Judges:")
        for config in judge_configs:
            print(f"  • {config['name']}: {config['model']}")
        
        # Analyze model distribution
        print(f"\n📊 Model Distribution Analysis:")
        model_counts = {}
        for model in player_models + judge_models:
            model_counts[model] = model_counts.get(model, 0) + 1
        
        for model, count in model_counts.items():
            print(f"  • {model}: {count} participants")
        
        # Create and start the game
        print("\n🎮 Creating mixed model game...")
        game = Game(
            player_configs=player_configs,
            judge_configs=judge_configs,
            model_config_manager=model_manager,
            enable_human_scoring=False  # Can be enabled for human evaluation
        )
        
        print("✅ Mixed model game created successfully!")
        
        # Display game information
        print(f"\n🎯 Game Setup Complete:")
        print(f"  Total participants: {len(game.players) + len(game.judge_panel.judges)}")
        print(f"  Unique models: {len(set(player_models + judge_models))}")
        print(f"  Model diversity: {len(set(player_models + judge_models)) / len(player_models + judge_models) * 100:.1f}%")
        
        # Show expected behavioral differences
        print(f"\n🧠 Expected Model Behaviors:")
        print("  • DeepSeek models: May show consistent reasoning patterns")
        print("  • GPT models: Typically strong at strategic thinking")
        print("  • Claude models: Often conservative and ethical in approach")
        print("  • Mixed setup allows for comparative analysis")
        
        print("\n🚀 Ready to start mixed model competition!")
        print("Note: Call game.play() to begin the actual game.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up mixed model game: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def create_mixed_model_presets():
    """Create various mixed model presets for different scenarios"""
    print("\n" + "=" * 60)
    print("Creating Mixed Model Presets")
    print("=" * 60)
    
    try:
        llm_client = LLMClient()
        model_manager = ModelConfigManager(llm_client)
        
        # Preset 1: Provider Comparison (OpenAI vs Anthropic)
        provider_comparison = {
            "preset_name": "provider_comparison",
            "description": "Direct comparison between OpenAI and Anthropic models",
            "player_configs": [
                {"name": "GPT-Alpha", "model": "openai/gpt-4o"},
                {"name": "GPT-Beta", "model": "openai/gpt-4o-mini"},
                {"name": "Claude-Alpha", "model": "anthropic/claude-3-5-sonnet"},
                {"name": "Claude-Beta", "model": "anthropic/claude-3-haiku"}
            ],
            "judge_configs": [
                {"name": "GPT-Justice", "model": "openai/gpt-4o"},
                {"name": "GPT-Wisdom", "model": "openai/gpt-4o-mini"},
                {"name": "Claude-Truth", "model": "anthropic/claude-3-5-sonnet"},
                {"name": "Claude-Honor", "model": "anthropic/claude-3-haiku"}
            ]
        }
        
        # Preset 2: Size Comparison (Large vs Small models)
        size_comparison = {
            "preset_name": "size_comparison_mixed",
            "description": "Compare large vs small models from different providers",
            "player_configs": [
                {"name": "Large-GPT", "model": "openai/gpt-4o"},
                {"name": "Small-GPT", "model": "openai/gpt-4o-mini"},
                {"name": "Large-Claude", "model": "anthropic/claude-3-5-sonnet"},
                {"name": "Small-Claude", "model": "anthropic/claude-3-haiku"}
            ],
            "judge_configs": [
                {"name": "Large-Judge-1", "model": "openai/gpt-4o"},
                {"name": "Small-Judge-1", "model": "openai/gpt-4o-mini"},
                {"name": "Large-Judge-2", "model": "anthropic/claude-3-5-sonnet"},
                {"name": "Small-Judge-2", "model": "anthropic/claude-3-haiku"}
            ]
        }
        
        # Preset 3: Research Diverse (Maximum diversity)
        research_diverse = {
            "preset_name": "research_diverse_mixed",
            "description": "Maximum model diversity for comprehensive research",
            "player_configs": [
                {"name": "DeepSeek-Player", "model": "deepseek-r1"},
                {"name": "GPT-Player", "model": "openai/gpt-4o"},
                {"name": "Claude-Player", "model": "anthropic/claude-3-5-sonnet"},
                {"name": "GPT-Mini-Player", "model": "openai/gpt-4o-mini"}
            ],
            "judge_configs": [
                {"name": "DeepSeek-Judge", "model": "deepseek-r1"},
                {"name": "GPT-Judge", "model": "openai/gpt-4o"},
                {"name": "Claude-Judge", "model": "anthropic/claude-3-5-sonnet"},
                {"name": "GPT-Mini-Judge", "model": "openai/gpt-4o-mini"}
            ]
        }
        
        # Save all presets
        presets = [
            ("provider_comparison", provider_comparison),
            ("size_comparison_mixed", size_comparison),
            ("research_diverse_mixed", research_diverse)
        ]
        
        for preset_name, preset_config in presets:
            model_manager.save_preset(preset_name, preset_config)
            print(f"✅ Created preset: {preset_name}")
        
        print(f"\n📋 Created {len(presets)} mixed model presets")
        return True
        
    except Exception as e:
        print(f"❌ Error creating presets: {str(e)}")
        return False


def demonstrate_model_comparison():
    """Demonstrate how to analyze model performance differences"""
    print("\n" + "=" * 60)
    print("Model Comparison Analysis")
    print("=" * 60)
    
    try:
        llm_client = LLMClient()
        model_manager = ModelConfigManager(llm_client)
        
        # Load a mixed model preset
        if "provider_comparison" in model_manager.list_presets():
            preset = model_manager.load_preset("provider_comparison")
            
            print(f"📖 Analyzing preset: {preset['preset_name']}")
            print(f"Description: {preset['description']}")
            
            # Analyze model distribution
            player_models = [config['model'] for config in preset['player_configs']]
            judge_models = [config['model'] for config in preset['judge_configs']]
            
            print(f"\n🔍 Model Analysis:")
            
            # Group by provider
            providers = {}
            for model in player_models + judge_models:
                if '/' in model:
                    provider = model.split('/')[0]
                else:
                    provider = 'other'
                
                if provider not in providers:
                    providers[provider] = []
                providers[provider].append(model)
            
            print("Provider distribution:")
            for provider, models in providers.items():
                unique_models = set(models)
                print(f"  • {provider}: {len(models)} participants, {len(unique_models)} unique models")
            
            # Expected comparison insights
            print(f"\n💡 Expected Comparison Insights:")
            print("  • Strategic differences between providers")
            print("  • Consistency within provider families")
            print("  • Performance variations by model size")
            print("  • Reasoning style differences")
            
        return True
        
    except Exception as e:
        print(f"❌ Error in model comparison: {str(e)}")
        return False


def main():
    """Main function to run all mixed model examples"""
    print("Mixed Model Game Examples")
    print("This script demonstrates various aspects of mixed model games.")
    print()
    
    success = True
    
    # Run mixed model game example
    if not run_mixed_model_game():
        success = False
    
    # Create presets example
    if not create_mixed_model_presets():
        success = False
    
    # Demonstrate model comparison
    if not demonstrate_model_comparison():
        success = False
    
    if success:
        print("\n🎉 All mixed model examples completed successfully!")
        print("\nKey takeaways:")
        print("• Mixed models enable comparative AI behavior analysis")
        print("• Different providers show distinct strategic approaches")
        print("• Model size affects decision-making complexity")
        print("• Presets facilitate reproducible research scenarios")
        print("• Validation ensures all models are available before starting")
    else:
        print("\n⚠️  Some examples encountered errors. Check the output above.")
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)