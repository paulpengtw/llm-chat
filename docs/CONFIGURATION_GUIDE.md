# Multi-LLM Debate System Configuration Guide

This guide provides comprehensive documentation for configuring and using the multi-LLM debate system, including model configurations, presets, and advanced options.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Model Configuration](#model-configuration)
3. [Preset Management](#preset-management)
4. [Human Scoring Configuration](#human-scoring-configuration)
5. [Error Handling Configuration](#error-handling-configuration)
6. [Advanced Configuration](#advanced-configuration)
7. [Best Practices](#best-practices)

## Quick Start

### Basic Single Model Game

```python
from game import Game
from model_config_manager import ModelConfigManager
from llm_client import LLMClient

# Initialize components
llm_client = LLMClient()
model_manager = ModelConfigManager(llm_client)

# Create simple configuration
player_configs = [
    {"name": "Player1", "model": "deepseek-r1"},
    {"name": "Player2", "model": "deepseek-r1"}
]

judge_configs = [
    {"name": "Judge1", "model": "deepseek-r1"},
    {"name": "Judge2", "model": "deepseek-r1"}
]

# Create and run game
game = Game(
    player_configs=player_configs,
    judge_configs=judge_configs,
    model_config_manager=model_manager
)
```

### Using Presets

```python
# Load existing preset
preset = model_manager.load_preset("single_model_test")

# Create game from preset
game = Game(
    player_configs=preset["player_configs"],
    judge_configs=preset["judge_configs"],
    model_config_manager=model_manager
)
```

## Model Configuration

### Supported Model Formats

The system supports various model naming conventions:

```python
# Provider/Model format (recommended)
"openai/gpt-4o"
"openai/gpt-4o-mini"
"anthropic/claude-3-5-sonnet"
"anthropic/claude-3-haiku"

# Direct model names
"deepseek-r1"
"gpt-4o"
"claude-3-sonnet"
```

### Model Validation

Always validate models before using them:

```python
# Validate single model
is_valid = model_manager.validate_model("openai/gpt-4o")

# Validate multiple models
models = ["openai/gpt-4o", "anthropic/claude-3-5-sonnet"]
for model in models:
    if not model_manager.validate_model(model):
        print(f"Model {model} is not available")
```

### Player Configuration

Player configurations specify which model each player uses:

```python
player_configs = [
    {
        "name": "Strategic-Player",    # Unique player name
        "model": "openai/gpt-4o"      # Model to use
    },
    {
        "name": "Creative-Player",
        "model": "anthropic/claude-3-5-sonnet"
    }
]

# Create configurations programmatically
models = ["openai/gpt-4o", "anthropic/claude-3-5-sonnet"]
names = ["GPT-Player", "Claude-Player"]
player_configs = model_manager.create_player_configs(models, names)
```

### Judge Configuration

Judge configurations work similarly to player configurations:

```python
judge_configs = [
    {
        "name": "Analytical-Judge",
        "model": "openai/gpt-4o"
    },
    {
        "name": "Intuitive-Judge",
        "model": "anthropic/claude-3-5-sonnet"
    }
]

# Judges can use the same model
judge_configs = model_manager.create_judge_configs(
    ["openai/gpt-4o", "openai/gpt-4o"],  # Same model for both
    ["Judge1", "Judge2"]
)
```

## Preset Management

### Preset Structure

Presets are JSON files that define complete game configurations:

```json
{
  "preset_name": "example_preset",
  "description": "Example preset for demonstration",
  "player_configs": [
    { "name": "Player1", "model": "openai/gpt-4o" },
    { "name": "Player2", "model": "anthropic/claude-3-5-sonnet" }
  ],
  "judge_configs": [
    { "name": "Judge1", "model": "openai/gpt-4o" },
    { "name": "Judge2", "model": "anthropic/claude-3-5-sonnet" }
  ]
}
```

### Creating Presets

#### Method 1: Programmatically

```python
preset_config = {
    "preset_name": "my_custom_preset",
    "description": "Custom preset for specific research",
    "player_configs": [
        {"name": "GPT-Player", "model": "openai/gpt-4o"},
        {"name": "Claude-Player", "model": "anthropic/claude-3-5-sonnet"}
    ],
    "judge_configs": [
        {"name": "GPT-Judge", "model": "openai/gpt-4o"},
        {"name": "Claude-Judge", "model": "anthropic/claude-3-5-sonnet"}
    ]
}

model_manager.save_preset("my_custom_preset", preset_config)
```

#### Method 2: Using Template Helper

```python
model_manager.create_custom_preset_from_template(
    preset_name="research_preset",
    template_type="mixed",
    player_models=["openai/gpt-4o", "anthropic/claude-3-5-sonnet"],
    judge_models=["openai/gpt-4o", "anthropic/claude-3-5-sonnet"],
    description="Research preset for provider comparison"
)
```

### Managing Presets

```python
# List all presets
presets = model_manager.list_presets()
print(f"Available presets: {presets}")

# Load preset
preset = model_manager.load_preset("preset_name")

# Validate preset models
validation_results = model_manager.validate_preset_models("preset_name")

# Validate all presets
all_results = model_manager.validate_all_presets()
```

### Built-in Presets

The system includes several built-in presets:

- **single_model_test**: All participants use the same model
- **gpt_vs_claude**: OpenAI vs Anthropic comparison
- **size_comparison**: Large vs small model comparison
- **mixed_providers**: Mixed provider configuration
- **research_diverse**: Maximum model diversity
- **research_extended**: Extended research configuration

## Human Scoring Configuration

### Enabling Human Scoring

```python
game = Game(
    player_configs=player_configs,
    judge_configs=judge_configs,
    model_config_manager=model_manager,
    enable_human_scoring=True,        # Enable human scoring
    human_scoring_port=5001           # Web interface port
)
```

### Human Scoring Interface

When human scoring is enabled:

1. **Web Interface**: Available at `http://127.0.0.1:5001` (or specified port)
2. **Scoring Criteria**:
   - Strategic Thinking (0-5)
   - Bluffing Skill (0-5)
   - Reasoning Quality (0-5)
   - Overall Performance (0-5)
3. **Timeout**: Configurable timeout for scoring sessions
4. **Real-time Updates**: Interface updates automatically when rounds need scoring

### Scoring Session Configuration

```python
# Configure scoring session parameters
interface = HumanScoringInterface(web_port=5001)

# Start scoring session with custom timeout
interface.start_scoring_session(
    round_info={"round_id": 1, "target_card": "K"},
    players=["Player1", "Player2"],
    timeout=300  # 5 minutes
)
```

## Error Handling Configuration

### Failure Handler Configuration

```python
from error_handling import ModelFailureHandler, create_default_fallback_configuration

# Configure failure handler
failure_handler = ModelFailureHandler(
    llm_client=llm_client,
    max_retries=3,           # Maximum retry attempts
    base_delay=1.0,          # Base delay between retries (seconds)
    max_delay=30.0,          # Maximum delay between retries
    backoff_factor=2.0       # Exponential backoff factor
)

# Set up fallback models
fallback_config = {
    "openai/gpt-4o": ["openai/gpt-4o-mini", "deepseek-r1"],
    "anthropic/claude-3-5-sonnet": ["anthropic/claude-3-haiku", "deepseek-r1"]
}
failure_handler.set_fallback_models(fallback_config)
```

### Graceful Degradation Configuration

```python
from error_handling import GracefulDegradationManager

degradation_manager = GracefulDegradationManager(
    default_timeout=30.0,           # Default timeout for model calls
    max_failed_players_ratio=0.5,   # Maximum ratio of failed players before stopping
    enable_fallback_responses=True,  # Enable fallback responses for failed models
    log_errors=True                 # Enable error logging
)
```

### Integrating Error Handling

```python
# ModelConfigManager automatically includes error handling
model_manager = ModelConfigManager(llm_client)

# Access error handling components
failure_handler = model_manager.get_failure_handler()
degradation_manager = model_manager.get_degradation_manager()

# Configure custom fallback models
model_manager.configure_fallback_models(fallback_config)
```

## Advanced Configuration

### Custom Model Validation

```python
class CustomModelConfigManager(ModelConfigManager):
    def validate_model(self, model_name: str, use_error_handling: bool = True) -> bool:
        # Custom validation logic
        if model_name.startswith("custom/"):
            return self._validate_custom_model(model_name)
        return super().validate_model(model_name, use_error_handling)

    def _validate_custom_model(self, model_name: str) -> bool:
        # Implement custom model validation
        pass
```

### Performance Monitoring

```python
# Get error statistics
error_stats = model_manager.get_error_statistics()
print(f"Failure statistics: {error_stats['failure_statistics']}")
print(f"Degradation status: {error_stats['degradation_status']}")

# Get model performance report
performance_report = degradation_manager.get_model_performance_report()
for model, stats in performance_report.items():
    print(f"{model}: {stats}")
```

### Custom Scoring Criteria

```python
# Extend HumanScoringInterface for custom criteria
class CustomScoringInterface(HumanScoringInterface):
    def __init__(self, web_port=5001, custom_criteria=None):
        super().__init__(web_port)
        self.custom_criteria = custom_criteria or [
            "strategic_thinking",
            "bluffing_skill",
            "reasoning_quality",
            "creativity",
            "adaptability",
            "overall_performance"
        ]
```

## Best Practices

### Model Selection

1. **Start Simple**: Begin with single model configurations for baseline testing
2. **Validate Early**: Always validate models before creating games
3. **Use Presets**: Leverage presets for reproducible configurations
4. **Mix Strategically**: Choose model combinations that highlight different approaches

### Configuration Management

1. **Version Control**: Store preset files in version control
2. **Documentation**: Document the purpose of each preset
3. **Validation**: Regularly validate presets to ensure models remain available
4. **Backup**: Keep backup configurations for critical research

### Error Handling

1. **Set Fallbacks**: Always configure fallback models for important scenarios
2. **Monitor Performance**: Regularly check error statistics and performance reports
3. **Adjust Timeouts**: Configure appropriate timeouts based on model performance
4. **Log Errors**: Enable comprehensive error logging for debugging

### Human Scoring

1. **Clear Criteria**: Provide clear scoring criteria to human judges
2. **Reasonable Timeouts**: Set appropriate timeouts for scoring sessions
3. **Multiple Judges**: Use multiple human judges for more reliable scoring
4. **Combine Perspectives**: Analyze both AI and human evaluation results

### Performance Optimization

1. **Parallel Validation**: Validate models in parallel when possible
2. **Cache Results**: Leverage model validation caching
3. **Efficient Presets**: Design presets to minimize redundant model calls
4. **Monitor Resources**: Track system resource usage during games

## Troubleshooting

### Common Issues

1. **Model Not Available**: Check model name spelling and availability
2. **Validation Failures**: Verify API keys and network connectivity
3. **Preset Loading Errors**: Check JSON syntax and required fields
4. **Human Scoring Timeout**: Increase timeout or check web interface accessibility

### Debug Mode

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Use error handling for detailed error information
result = model_manager.validate_model("model-name", use_error_handling=True)
```

### Getting Help

1. **Check Logs**: Review error logs for detailed information
2. **Validate Configuration**: Use validation tools to check configurations
3. **Test Components**: Test individual components in isolation
4. **Review Examples**: Check example scripts for reference implementations

## Configuration Examples

See the `examples/` directory for complete configuration examples:

- `example_single_model_game.py`: Single model configuration
- `example_mixed_model_game.py`: Mixed model configuration
- `example_human_scoring_game.py`: Human scoring integration

Each example includes detailed comments and error handling demonstrations.
