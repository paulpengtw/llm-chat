#!/usr/bin/env python3
"""
Example: Human Scoring Integration

This example demonstrates how to run a game with human scoring enabled,
allowing human judges to evaluate LLM performance alongside AI judges.

Requirements covered: 3.1, 3.2, 1.3
"""

import sys
import os
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game import Game
from model_config_manager import ModelConfigManager
from human_scoring_interface import HumanScoringInterface
from llm_client import LLMClient


def run_game_with_human_scoring():
    """Run a game with human scoring enabled"""
    print("=" * 60)
    print("Human Scoring Integration Example")
    print("=" * 60)
    print("This example demonstrates human scoring integration with multi-model games.")
    print("Human judges can score LLM performance alongside AI judges.")
    print()
    
    try:
        # Initialize components
        print("🔧 Initializing components...")
        llm_client = LLMClient()
        model_manager = ModelConfigManager(llm_client)
        
        # Define models for a mixed game
        player_models = ["deepseek-r1", "openai/gpt-4o-mini"]
        player_names = ["DeepSeek-Player", "GPT-Player"]
        
        judge_models = ["deepseek-r1", "openai/gpt-4o-mini"]
        judge_names = ["DeepSeek-Judge", "GPT-Judge"]
        
        print("🔍 Validating models...")
        
        # Validate models
        all_models = set(player_models + judge_models)
        for model in all_models:
            if not model_manager.validate_model(model):
                print(f"❌ Model '{model}' is not available.")
                print("Please update model names or check configuration.")
                return False
        
        print("✅ All models validated!")
        
        # Create configurations
        print("👥 Creating configurations...")
        player_configs = model_manager.create_player_configs(player_models, player_names)
        judge_configs = model_manager.create_judge_configs(judge_models, judge_names)
        
        # Display configuration
        print("\n📋 Game Configuration with Human Scoring:")
        print("Players:")
        for config in player_configs:
            print(f"  • {config['name']}: {config['model']}")
        
        print("AI Judges:")
        for config in judge_configs:
            print(f"  • {config['name']}: {config['model']}")
        
        print("Human Judges:")
        print("  • You (via web interface)")
        
        # Create game with human scoring enabled
        print("\n🎮 Creating game with human scoring...")
        game = Game(
            player_configs=player_configs,
            judge_configs=judge_configs,
            model_config_manager=model_manager,
            enable_human_scoring=True,
            human_scoring_port=5001  # Default port
        )
        
        print("✅ Game created with human scoring enabled!")
        
        # Display human scoring information
        print(f"\n🌐 Human Scoring Interface:")
        print(f"  URL: http://127.0.0.1:5001")
        print(f"  Status: Ready for scoring sessions")
        
        # Demonstrate scoring session setup
        print(f"\n📝 Scoring Session Setup:")
        print("When a round completes, the system will:")
        print("  1. Display round information on the web interface")
        print("  2. Allow you to score each player on multiple criteria:")
        print("     • Strategic Thinking (0-5)")
        print("     • Bluffing Skill (0-5)")
        print("     • Reasoning Quality (0-5)")
        print("     • Overall Performance (0-5)")
        print("  3. Combine your scores with AI judge evaluations")
        print("  4. Display comprehensive round summary")
        
        # Show scoring criteria explanation
        print(f"\n🎯 Scoring Criteria Guide:")
        print("Strategic Thinking:")
        print("  • 5: Excellent long-term planning and tactical awareness")
        print("  • 3: Good strategic decisions with minor flaws")
        print("  • 1: Poor strategic thinking, reactive play")
        print("  • 0: No apparent strategic consideration")
        
        print("Bluffing Skill:")
        print("  • 5: Masterful deception and misdirection")
        print("  • 3: Effective bluffing with some tells")
        print("  • 1: Obvious or ineffective bluffing attempts")
        print("  • 0: No bluffing or completely transparent")
        
        print("Reasoning Quality:")
        print("  • 5: Clear, logical, well-articulated reasoning")
        print("  • 3: Generally sound reasoning with minor gaps")
        print("  • 1: Flawed or inconsistent reasoning")
        print("  • 0: No clear reasoning provided")
        
        print("Overall Performance:")
        print("  • 5: Outstanding overall gameplay")
        print("  • 3: Solid performance with room for improvement")
        print("  • 1: Below average performance")
        print("  • 0: Poor overall performance")
        
        print(f"\n🚀 Human scoring game setup complete!")
        print("Note: In a real game, you would call game.play() to start.")
        print("The web interface will automatically update when rounds need scoring.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up human scoring game: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def demonstrate_scoring_interface():
    """Demonstrate the human scoring interface functionality"""
    print("\n" + "=" * 60)
    print("Human Scoring Interface Demonstration")
    print("=" * 60)
    
    try:
        # Create scoring interface
        print("🌐 Creating human scoring interface...")
        interface = HumanScoringInterface(web_port=5002)  # Use different port
        
        # Simulate a scoring session
        print("📝 Simulating scoring session...")
        
        round_info = {
            "round_id": 1,
            "target_card": "K",
            "starting_player": "DeepSeek-Player",
            "round_players": ["DeepSeek-Player", "GPT-Player"],
            "model_assignments": {
                "DeepSeek-Player": "deepseek-r1",
                "GPT-Player": "openai/gpt-4o-mini"
            }
        }
        
        players = ["DeepSeek-Player", "GPT-Player"]
        
        # Start scoring session
        interface.start_scoring_session(round_info, players, timeout=60)
        
        print(f"✅ Scoring session started!")
        print(f"🌐 Interface available at: http://127.0.0.1:5002")
        print(f"⏱️  Session timeout: 60 seconds")
        
        # Display session information
        print(f"\n📊 Session Information:")
        print(f"  Round ID: {round_info['round_id']}")
        print(f"  Target Card: {round_info['target_card']}")
        print(f"  Players to Score: {', '.join(players)}")
        
        # Simulate AI judge votes for comparison
        ai_votes = {
            "votes": {
                "DeepSeek-Judge": {
                    "voted_player": "DeepSeek-Player",
                    "reasoning": "Excellent strategic thinking and consistent reasoning"
                },
                "GPT-Judge": {
                    "voted_player": "GPT-Player", 
                    "reasoning": "Strong bluffing skills and adaptive gameplay"
                }
            }
        }
        
        print(f"\n🤖 AI Judge Votes (for comparison):")
        for judge, vote in ai_votes["votes"].items():
            print(f"  {judge}: {vote['voted_player']}")
            print(f"    Reasoning: {vote['reasoning']}")
        
        # Simulate human scores (in real scenario, these come from web interface)
        human_scores = {
            "DeepSeek-Player": {
                "strategic_thinking": 4,
                "bluffing_skill": 3,
                "reasoning_quality": 5,
                "overall_performance": 4
            },
            "GPT-Player": {
                "strategic_thinking": 3,
                "bluffing_skill": 5,
                "reasoning_quality": 4,
                "overall_performance": 4
            }
        }
        
        print(f"\n👤 Example Human Scores:")
        for player, scores in human_scores.items():
            print(f"  {player}:")
            for criterion, score in scores.items():
                criterion_display = criterion.replace('_', ' ').title()
                print(f"    {criterion_display}: {score}/5")
            avg = sum(scores.values()) / len(scores)
            print(f"    Average: {avg:.1f}/5")
        
        # Display combined summary
        interface.display_round_summary(round_info, ai_votes, human_scores)
        
        # Show statistics
        stats = interface.get_scoring_statistics()
        print(f"\n📈 Scoring Statistics:")
        for key, value in stats.items():
            print(f"  {key.replace('_', ' ').title()}: {value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error demonstrating scoring interface: {str(e)}")
        return False


def create_human_scoring_preset():
    """Create a preset optimized for human scoring scenarios"""
    print("\n" + "=" * 60)
    print("Creating Human Scoring Preset")
    print("=" * 60)
    
    try:
        llm_client = LLMClient()
        model_manager = ModelConfigManager(llm_client)
        
        # Create preset optimized for human evaluation
        human_scoring_preset = {
            "preset_name": "human_scoring_optimized",
            "description": "Optimized configuration for human scoring evaluation with diverse models",
            "player_configs": [
                {"name": "Conservative-AI", "model": "anthropic/claude-3-5-sonnet"},
                {"name": "Aggressive-AI", "model": "openai/gpt-4o"},
                {"name": "Balanced-AI", "model": "deepseek-r1"},
                {"name": "Adaptive-AI", "model": "openai/gpt-4o-mini"}
            ],
            "judge_configs": [
                {"name": "Analytical-Judge", "model": "openai/gpt-4o"},
                {"name": "Intuitive-Judge", "model": "anthropic/claude-3-5-sonnet"},
                {"name": "Balanced-Judge", "model": "deepseek-r1"},
                {"name": "Quick-Judge", "model": "openai/gpt-4o-mini"}
            ],
            "human_scoring_config": {
                "enabled": True,
                "timeout_seconds": 300,
                "criteria": [
                    "strategic_thinking",
                    "bluffing_skill", 
                    "reasoning_quality",
                    "overall_performance"
                ],
                "scale": "0-5"
            }
        }
        
        # Save the preset
        model_manager.save_preset("human_scoring_optimized", human_scoring_preset)
        print("✅ Created human scoring preset: human_scoring_optimized")
        
        # Display preset details
        print(f"\n📋 Preset Details:")
        print(f"  Name: {human_scoring_preset['preset_name']}")
        print(f"  Description: {human_scoring_preset['description']}")
        print(f"  Players: {len(human_scoring_preset['player_configs'])}")
        print(f"  Judges: {len(human_scoring_preset['judge_configs'])}")
        print(f"  Human Scoring: Enabled")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating human scoring preset: {str(e)}")
        return False


def main():
    """Main function to run all human scoring examples"""
    print("Human Scoring Integration Examples")
    print("This script demonstrates human scoring integration with multi-model games.")
    print()
    
    success = True
    
    # Run human scoring game example
    if not run_game_with_human_scoring():
        success = False
    
    # Demonstrate scoring interface
    if not demonstrate_scoring_interface():
        success = False
    
    # Create human scoring preset
    if not create_human_scoring_preset():
        success = False
    
    if success:
        print("\n🎉 All human scoring examples completed successfully!")
        print("\nKey takeaways:")
        print("• Human scoring provides subjective evaluation alongside AI judges")
        print("• Web interface makes scoring accessible and user-friendly")
        print("• Multiple criteria allow comprehensive performance assessment")
        print("• Combined AI and human evaluation gives complete picture")
        print("• Presets can include human scoring configuration")
        print("\nTo use human scoring in your games:")
        print("1. Enable human_scoring=True when creating games")
        print("2. Open the web interface URL when prompted")
        print("3. Score players on each criterion (0-5 scale)")
        print("4. Review combined AI and human evaluation results")
    else:
        print("\n⚠️  Some examples encountered errors. Check the output above.")
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)