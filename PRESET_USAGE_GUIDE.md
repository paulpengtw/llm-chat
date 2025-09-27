# Model Configuration Preset Usage Guide

This guide explains how to use the model configuration preset system for multi-LLM debates.

## Overview

The preset system allows you to easily configure different combinations of LLM models for players and judges in the card game. This enables comparative studies of AI behavior and strategic decision-making across different models.

## Available Presets

### Single Model Presets

- **`single_gpt4o`**: All players and judges use GPT-4o for baseline testing
- **`single_claude`**: All players and judges use Claude-3.5-Sonnet for baseline testing
- **`single_model_test`**: Generic single model preset (currently uses GPT-4o)

### Provider Comparison Presets

- **`gpt_vs_claude`**: OpenAI GPT models vs Anthropic Claude models head-to-head comparison
- **`mixed_providers`**: Mixed provider configuration with OpenAI and Anthropic models
- **`size_comparison`**: Compare large vs small models from same providers

### Research Presets

- **`research_diverse`**: Diverse model comparison for research with different providers and sizes
- **`research_extended`**: Extended research configuration with additional model options
- **`mixed_models_example`**: Example configuration with different models (template)

## Using Presets in Code

### Basic Usage

```python
from model_config_manager import ModelConfigManager
from llm_client import LLMClient

# Initialize the manager
llm_client = LLMClient()
manager = ModelConfigManager(llm_client)

# Load a preset
preset = manager.load_preset("gpt_vs_claude")

# Extract configurations
player_configs = preset["player_configs"]
judge_configs = preset["judge_configs"]

# Use in game initialization
# (Integration with Game class depends on your specific implementation)
```

### Validating Presets

```python
# Validate all models in a preset
validation_results = manager.validate_preset_models("gpt_vs_claude")
print(validation_results)

# Validate all available presets
all_validations = manager.validate_all_presets()
for preset_name, results in all_validations.items():
    if results["all_models_valid"]:
        print(f"✅ {preset_name}: All models valid")
    else:
        print(f"❌ {preset_name}: Some models invalid")
```

### Listing Available Presets

```python
# List all preset names
presets = manager.list_presets()
print(f"Available presets: {presets}")

# Get preset recommendations for different scenarios
recommendations = manager.get_preset_recommendations()
print(recommendations)
```

## Creating Custom Presets

### Method 1: Using the Template System

```python
# Create a custom preset from template
manager.create_custom_preset_from_template(
    preset_name="my_custom_preset",
    template_type="research",
    player_models=["openai/gpt-4o", "anthropic/claude-3-5-sonnet", "openai/gpt-4o-mini", "anthropic/claude-3-haiku"],
    judge_models=["openai/gpt-4o", "anthropic/claude-3-5-sonnet", "openai/gpt-4o", "anthropic/claude-3-5-sonnet"],
    description="My custom research configuration"
)
```

### Method 2: Manual Configuration

```python
# Create a custom preset manually
custom_preset = {
    "preset_name": "my_preset",
    "description": "Custom configuration for specific research",
    "player_configs": [
        {"name": "Player-A", "model": "openai/gpt-4o"},
        {"name": "Player-B", "model": "anthropic/claude-3-5-sonnet"},
        {"name": "Player-C", "model": "openai/gpt-4o-mini"},
        {"name": "Player-D", "model": "anthropic/claude-3-haiku"}
    ],
    "judge_configs": [
        {"name": "Judge-1", "model": "openai/gpt-4o"},
        {"name": "Judge-2", "model": "anthropic/claude-3-5-sonnet"},
        {"name": "Judge-3", "model": "openai/gpt-4o-mini"},
        {"name": "Judge-4", "model": "anthropic/claude-3-haiku"}
    ]
}

# Save the preset
manager.save_preset("my_preset", custom_preset)
```

## Preset Structure

Each preset is a JSON file with the following structure:

```json
{
  "preset_name": "preset_identifier",
  "description": "Human-readable description of the preset",
  "player_configs": [
    {
      "name": "Player-Name",
      "model": "provider/model-name"
    }
  ],
  "judge_configs": [
    {
      "name": "Judge-Name",
      "model": "provider/model-name"
    }
  ]
}
```

### Requirements

- Maximum 4 players and 4 judges
- Each config must have `name` and `model` fields
- Model names should follow the provider/model-name format
- Player and judge names should be unique within their respective groups

## Model Name Formats

The system supports various model name formats:

### OpenAI Models

- `openai/gpt-4o`
- `openai/gpt-4o-mini`
- `gpt-4o` (shorthand)
- `gpt-4o-mini` (shorthand)

### Anthropic Models

- `anthropic/claude-3-5-sonnet`
- `anthropic/claude-3-haiku`
- `claude-3-sonnet` (shorthand)
- `claude-3-haiku` (shorthand)

### Other Providers

- `deepseek/deepseek-r1`
- `provider/model-name` (generic format)

## Error Handling

The preset system includes comprehensive error handling:

### Validation Errors

- Invalid JSON format
- Missing required fields
- Invalid model names
- Too many players/judges (>4)
- Duplicate names

### Runtime Errors

- Model API failures
- Network connectivity issues
- Authentication problems

### Fallback Strategies

- Retry logic with exponential backoff
- Fallback model configurations
- Graceful degradation when models fail

## Best Practices

### For Research

1. **Start with single-model presets** to establish baselines
2. **Use provider comparison presets** to compare different AI approaches
3. **Create custom presets** for specific research questions
4. **Validate all models** before starting experiments

### For Development

1. **Use `single_model_test`** for initial development and testing
2. **Test with `mixed_models_example`** to verify multi-model functionality
3. **Create development-specific presets** with reliable, fast models

### For Production

1. **Validate presets** before deployment
2. **Configure fallback models** for error handling
3. **Monitor model performance** and availability
4. **Keep preset documentation** up to date

## Troubleshooting

### Common Issues

**Preset not found**

```
FileNotFoundError: Preset 'my_preset' not found
```

- Check preset name spelling
- Verify preset file exists in `model_presets/` directory
- Use `manager.list_presets()` to see available presets

**Model validation failed**

```
ValueError: Invalid models: model-name
```

- Check model name format
- Verify model is available through your LLM client
- Check API credentials and permissions

**Invalid preset structure**

```
ValueError: Missing required field 'player_configs'
```

- Verify JSON structure matches required format
- Check all required fields are present
- Validate JSON syntax

### Getting Help

1. **Run validation**: Use `python3 test_presets.py` to validate all presets
2. **Check logs**: Look for detailed error messages in console output
3. **Test models**: Use `manager.validate_model()` to test individual models
4. **Review examples**: Look at existing preset files for reference

## Integration Examples

### With Game Class

```python
# Example integration (adapt to your Game class)
def create_game_from_preset(preset_name: str):
    manager = ModelConfigManager(LLMClient())
    preset = manager.load_preset(preset_name)

    # Create players with model assignments
    players = []
    for config in preset["player_configs"]:
        player = Player(
            name=config["name"],
            model=config["model"],
            llm_client=manager.llm_client
        )
        players.append(player)

    # Create judges with model assignments
    judges = []
    for config in preset["judge_configs"]:
        judge = Judge(
            name=config["name"],
            model=config["model"],
            llm_client=manager.llm_client
        )
        judges.append(judge)

    # Initialize game
    game = Game(players=players, judges=judges)
    return game
```

This preset system provides a flexible and robust foundation for conducting multi-LLM research and comparisons in the card game environment.
