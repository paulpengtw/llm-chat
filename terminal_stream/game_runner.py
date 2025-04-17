import os
import sys
from stream_handler import init_stream

# Get project root directory and add to path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

# Change working directory to project root for prompt file access
os.chdir(root_dir)

# Import required modules
from game import Game
from json_convert import convert_game_record_to_chinese_text
import glob

def run_game():
    """Run the game with our stream handler"""
    init_stream()  # Initialize our output stream
    
    print("\n" + "="*50)
    print("Starting new game session")
    print("="*50 + "\n")

    # Configure players
    player_configs = [
        {
            "name": "Hearts",
            "model": "openai/gpt-4o-mini"
        },
        {
            "name": "Spades",
            "model": "openai/gpt-4o-mini"
        },
        {
            "name": "Diamonds",
            "model": "openai/gpt-4o-mini"
        },
        {
            "name": "Clubs",
            "model": "openai/gpt-4o-mini"
        }
    ]

    # Configure judges
    judge_configs = [
        {
            "name": "Justice",
            "model": "openai/gpt-4o-mini"
        },
        {
            "name": "Wisdom",
            "model": "openai/gpt-4o-mini"
        }
    ]

    print("Game started!")
    print("\nPlayer configurations:")
    for config in player_configs:
        print(f"Player: {config['name']}, Using model: {config['model']}")
    
    print("\nJudge configurations:")
    for config in judge_configs:
        print(f"Judge: {config['name']}, Using model: {config['model']}")
    print("-" * 50 + "\n")

    # Create and start the game
    game = Game(player_configs, judge_configs)
    game.start_game()

    # After game ends, convert and display the latest game record
    game_records = sorted(glob.glob('game_records/*.json'))
    if game_records:
        latest_record = game_records[-1]
        print("\n" + "="*50)
        print(f"Converting game record: {latest_record}")
        print("="*50 + "\n")
        
        # Convert and print the game record
        chinese_text = convert_game_record_to_chinese_text(latest_record)
        print(chinese_text)

if __name__ == "__main__":
    run_game()
