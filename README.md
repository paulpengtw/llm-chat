# LLM Card Game with Real-time Web Display

An innovative card game where LLM players compete using strategic decision-making and social deduction mechanics. The game features an advanced judge panel system and real-time web-based output display.

## Game Overview

This is a social deduction card game played by LLM agents. Players must make strategic decisions about playing cards and challenging others' plays, while a panel of LLM judges evaluates their performance.

### Key Components

- **Player System**: LLM-powered players that can make strategic decisions and reflect on game state
- **Judge Panel**: A group of LLM judges that evaluate player performance and maintain scoring
- **Game Records**: Detailed tracking and Chinese-text conversion of game events
- **Web Interface**: Real-time streaming display of game progress

## Project Structure

```
project_root/
├── game.py             # Core game logic and main game loop
├── player.py           # Player class with LLM decision making
├── judge_panel.py      # Judge evaluation system
├── game_record.py      # Game state recording
├── json_convert.py     # Convert game records to readable format
├── prompt/            # LLM prompt templates
│   ├── challenge_prompt_template.txt
│   ├── judge_prompt_template.txt
│   ├── play_card_prompt_template.txt
│   ├── reflect_prompt_template.txt
│   └── rule_base.txt
└── terminal_stream/    # Web interface for output display
    ├── main.py           # Flask server with SSE support
    ├── stream_handler.py # Global output stream handler
    ├── game_runner.py    # Game execution in project context
    └── index.html       # Web interface template (embedded in main.py)
```

## Web Interface Features

The terminal_stream module provides real-time visualization of game progress:
- Real-time streaming of terminal output to a web browser
- Automatic handling of Chinese characters and special formatting symbols
- Continuous auto-scrolling with optimized performance
- Support for handling both text and binary output
- Clean display of game state, player actions, and final results

### Usage

1. Start the web interface:
```bash
cd terminal_stream
python3 main.py
```

2. Open browser at `http://localhost:5000`

3. The game will automatically start and all output will be streamed to the browser window in real-time.

### Implementation Details

- Uses Flask for the web server with Server-Sent Events (SSE) for real-time updates
- Custom stream handler captures all stdout and streams it to connected clients
- Handles special characters and formatting for game state representation
- Converts Chinese text and game symbols to web-safe formats
- Implements efficient auto-scrolling with null message keep-alive system

### Notes

- The game output is not persisted - closing the browser window will clear the display
- Uses port 5000 by default
- Requires Python 3.x and Flask

### Debugging LLM Responses

The Player class includes a built-in debug output system to help diagnose LLM response issues:

- Location: `player.py` in the `choose_cards_to_play` method
- Purpose: Helps diagnose validation issues with LLM responses
- What it tracks:
  - Prompts sent to the LLM
  - Raw responses received
  - JSON structure validation
  - Card play validation (hand contents and count limits)
- Usage: Uncomment the debug print statements in the marked DEBUG OUTPUT section
- When to use: 
  - When investigating LLM response parsing failures
  - When validating game rule compliance
  - During development of new game mechanics
  - When troubleshooting card play logic

## Requirements

- Python 3.x
- OpenAI API access (for LLM functionality)
- Required Python packages:
  - openai
  - flask
  - python-dotenv

## Setup

1. Clone the repository
2. Install dependencies
3. Create a `.env` file with your API credentials
4. Run with either the standard terminal output or the new web interface

## License

See the LICENSE file for details.
