# Human Scoring Interface

The Human Scoring Interface provides a web-based system for human judges to evaluate LLM performance during multi-LLM debate card games.

## Features

- **Web-based Interface**: Clean, responsive web interface accessible via browser
- **Real-time Scoring**: Live score collection with immediate validation
- **Multiple Criteria**: Score players on strategic thinking, bluffing skill, reasoning quality, and overall performance
- **Session Management**: Automatic session handling with timeout protection
- **Progress Tracking**: Visual progress indicators and timer
- **Score Validation**: 0-5 scale validation with error handling
- **Responsive Design**: Works on desktop, tablet, and mobile devices

## Quick Start

1. **Import and Initialize**:

```python
from human_scoring_interface import HumanScoringInterface

# Create interface (default port 5001)
interface = HumanScoringInterface(web_port=5001)
```

2. **Start a Scoring Session**:

```python
round_info = {
    "round_id": 1,
    "target_card": "K",
    "starting_player": "Alice",
    "round_players": ["Alice", "Bob", "Charlie", "Diana"]
}

players = ["Alice", "Bob", "Charlie", "Diana"]

# Start session with 5-minute timeout
interface.start_scoring_session(round_info, players, timeout=300)
```

3. **Collect Scores**:

```python
# This blocks until scores are submitted or timeout
scores = interface.collect_scores(timeout=300)

# scores format:
# {
#     "Alice": {
#         "strategic_thinking": 4,
#         "bluffing_skill": 3,
#         "reasoning_quality": 5,
#         "overall_performance": 4
#     },
#     "Bob": { ... }
# }
```

4. **Display Results**:

```python
# Show combined AI and human evaluation results
interface.display_round_summary(round_info, ai_votes, scores)
```

## Web Interface

Once a scoring session starts, human judges can access the interface at:
`http://127.0.0.1:5001` (or your configured port)

### Scoring Criteria

Each player is evaluated on a 0-5 scale across four criteria:

- **Strategic Thinking** (0-5): How well the player planned and executed strategy
- **Bluffing Skill** (0-5): Effectiveness of deception and misdirection
- **Reasoning Quality** (0-5): Logical consistency and explanation quality
- **Overall Performance** (0-5): General effectiveness in the round

### Interface Features

- **Timer**: Shows remaining time for scoring session
- **Progress Bar**: Visual indicator of scoring completion
- **Player Cards**: Individual scoring forms for each player
- **Real-time Validation**: Immediate feedback on score submissions
- **Responsive Design**: Adapts to different screen sizes

## API Endpoints

The interface provides REST API endpoints:

- `GET /`: Main scoring interface page
- `GET /api/session`: Get current session data
- `POST /api/submit_score`: Submit scores for a player
- `GET /api/statistics`: Get scoring statistics

## Testing

Run the test script to verify functionality:

```bash
python3 test_human_scoring.py
```

This will:

1. Start a test scoring session
2. Open web interface for manual testing
3. Collect and display results
4. Show scoring statistics

## Integration with Game System

The Human Scoring Interface integrates with the existing judge panel system:

```python
# In your game class
from human_scoring_interface import HumanScoringInterface

class Game:
    def __init__(self, player_configs, judge_configs, enable_human_scoring=False):
        # ... existing initialization ...

        if enable_human_scoring:
            self.human_scoring = HumanScoringInterface()
            self.judge_panel.set_human_scoring_interface(self.human_scoring)

    def reset_round(self, use_current_player):
        # ... existing round reset logic ...

        # Get round info for evaluation
        round_info = {
            "base_info": self.game_record.get_latest_round_info(),
            "action_info": self.game_record.get_latest_round_actions(None, include_latest=True)
        }

        # AI judge evaluation
        self.judge_panel.evaluate_round(round_info)
        ai_votes = self.judge_panel.reveal_votes()

        # Human scoring (if enabled)
        human_scores = {}
        if hasattr(self, 'human_scoring'):
            alive_players = [p.name for p in self.players if p.alive]
            self.human_scoring.start_scoring_session(round_info["base_info"], alive_players)
            human_scores = self.human_scoring.collect_scores()

            # Display combined results
            self.human_scoring.display_round_summary(
                round_info["base_info"], ai_votes, human_scores
            )

        # ... continue with existing logic ...
```

## Configuration

### Port Configuration

```python
# Use different port
interface = HumanScoringInterface(web_port=8080)
```

### Timeout Settings

```python
# Start session with custom timeout (in seconds)
interface.start_scoring_session(round_info, players, timeout=600)  # 10 minutes

# Collect scores with custom timeout
scores = interface.collect_scores(timeout=600)
```

## Requirements

- Python 3.7+
- Flask 2.0+
- Modern web browser with JavaScript enabled

## File Structure

```
human_scoring_interface.py      # Main interface class
templates/human_scoring.html    # Standalone HTML interface
test_human_scoring.py          # Test script
HUMAN_SCORING_README.md        # This documentation
```

## Troubleshooting

### Common Issues

1. **Port Already in Use**: Change the port number in initialization
2. **Flask Not Found**: Install Flask with `pip install flask`
3. **Timeout Issues**: Increase timeout values for slower scoring
4. **Browser Compatibility**: Use modern browsers (Chrome, Firefox, Safari, Edge)

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

- Multiple human judges per session
- Custom scoring criteria
- Score export functionality
- Integration with game analytics
- Mobile app interface
