# Multi-LLM Debate System Examples

This directory contains comprehensive examples demonstrating different aspects of the multi-LLM debate system. Each example is self-contained and includes detailed comments explaining the concepts and implementation.

## Overview

The examples are organized by functionality and complexity:

1. **Basic Examples**: Simple configurations for getting started
2. **Advanced Examples**: Complex scenarios with multiple models and features
3. **Integration Examples**: Demonstrations of system integration and workflows

## Example Files

### Core Functionality Examples

#### `example_single_model_game.py`

**Purpose**: Demonstrates single model game configuration where all players and judges use the same LLM model.

**Key Features**:

- Basic game setup with uniform model configuration
- Model validation and error handling
- Preset creation and management
- Baseline testing scenarios

**Use Cases**:

- Establishing baseline behavior for a specific model
- Testing game mechanics without model variability
- Comparing different versions of the same model
- Educational demonstrations

**Run Example**:

```bash
python3 examples/example_single_model_game.py
```

#### `example_mixed_model_game.py`

**Purpose**: Demonstrates mixed model games with different LLM models competing against each other.

**Key Features**:

- Multi-model player and judge configuration
- Provider comparison (OpenAI vs Anthropic vs others)
- Model size comparison (large vs small models)
- Diversity analysis and statistics

**Use Cases**:

- Comparative analysis of different AI approaches
- Research on model behavior differences
- Provider performance evaluation
- Strategic gameplay analysis

**Run Example**:

```bash
python3 examples/example_mixed_model_game.py
```

#### `example_human_scoring_game.py`

**Purpose**: Demonstrates human scoring integration with multi-model games.

**Key Features**:

- Human scoring interface setup
- Web-based scoring forms
- Combined AI and human evaluation
- Scoring criteria and guidelines

**Use Cases**:

- Subjective evaluation of LLM performance
- Human-AI evaluation comparison
- Research requiring human judgment
- Quality assessment and validation

**Run Example**:

```bash
python3 examples/example_human_scoring_game.py
```

## Quick Start Guide

### Prerequisites

1. **Install Dependencies**: Ensure all required packages are installed
2. **Configure API Keys**: Set up API keys for LLM providers
3. **Verify Models**: Check that your desired models are available

### Running Examples

1. **Choose an Example**: Select based on your use case
2. **Review Code**: Read through the example to understand the concepts
3. **Modify Configuration**: Update model names and settings as needed
4. **Run the Example**: Execute the script and observe the output

### Basic Workflow

```python
# 1. Import required components
from game import Game
from model_config_manager import ModelConfigManager
from llm_client import LLMClient

# 2. Initialize components
llm_client = LLMClient()
model_manager = ModelConfigManager(llm_client)

# 3. Configure models
player_configs = [
    {"name": "Player1", "model": "your-model-name"},
    {"name": "Player2", "model": "your-model-name"}
]

# 4. Create and run game
game = Game(
    player_configs=player_configs,
    judge_configs=judge_configs,
    model_config_manager=model_manager
)
```

## Example Scenarios

### Scenario 1: Model Comparison Research

**Objective**: Compare performance between different LLM providers

**Configuration**:

```python
# Use example_mixed_model_game.py with provider comparison preset
player_models = [
    "openai/gpt-4o",              # OpenAI large model
    "openai/gpt-4o-mini",         # OpenAI small model
    "anthropic/claude-3-5-sonnet", # Anthropic large model
    "anthropic/claude-3-haiku"     # Anthropic small model
]
```

**Expected Insights**:

- Strategic thinking differences between providers
- Performance variations by model size
- Consistency within provider families
- Cost vs performance trade-offs

### Scenario 2: Baseline Establishment

**Objective**: Establish baseline behavior for a specific model

**Configuration**:

```python
# Use example_single_model_game.py
model_name = "deepseek-r1"  # Use same model for all participants
```

**Expected Insights**:

- Consistent behavior patterns
- Model-specific strategic preferences
- Reproducible game outcomes
- Performance benchmarks

### Scenario 3: Human Evaluation Study

**Objective**: Conduct human evaluation of LLM performance

**Configuration**:

```python
# Use example_human_scoring_game.py with diverse models
enable_human_scoring = True
scoring_criteria = [
    "strategic_thinking",
    "bluffing_skill",
    "reasoning_quality",
    "overall_performance"
]
```

**Expected Insights**:

- Human vs AI evaluation differences
- Subjective performance assessment
- Model strengths and weaknesses
- Quality validation metrics

## Customization Guide

### Modifying Model Configurations

#### Update Model Names

```python
# Replace with your available models
player_models = [
    "your-model-1",
    "your-model-2",
    "your-model-3",
    "your-model-4"
]
```

#### Add Model Validation

```python
# Always validate models before use
invalid_models = []
for model in player_models:
    if not model_manager.validate_model(model):
        invalid_models.append(model)

if invalid_models:
    print(f"Invalid models: {invalid_models}")
    # Handle invalid models appropriately
```

### Creating Custom Presets

#### Define Custom Configuration

```python
custom_preset = {
    "preset_name": "my_research_preset",
    "description": "Custom preset for specific research",
    "player_configs": [
        {"name": "Experimental-AI", "model": "experimental-model"},
        {"name": "Baseline-AI", "model": "baseline-model"}
    ],
    "judge_configs": [
        {"name": "Expert-Judge", "model": "expert-model"},
        {"name": "Standard-Judge", "model": "standard-model"}
    ]
}

# Save for reuse
model_manager.save_preset("my_research_preset", custom_preset)
```

### Enabling Advanced Features

#### Error Handling Configuration

```python
# Configure fallback models
fallback_config = {
    "primary-model": ["fallback-model-1", "fallback-model-2"],
    "expensive-model": ["cheaper-model"]
}
model_manager.configure_fallback_models(fallback_config)
```

#### Human Scoring Customization

```python
# Custom scoring interface
interface = HumanScoringInterface(
    web_port=5001,
    timeout_seconds=600  # 10 minutes
)

# Custom scoring criteria
custom_criteria = [
    "strategic_thinking",
    "creativity",
    "adaptability",
    "communication_clarity"
]
```

## Best Practices

### Model Selection

1. **Start Simple**: Begin with single model configurations
2. **Validate Early**: Always validate models before creating games
3. **Use Presets**: Leverage presets for reproducible configurations
4. **Document Choices**: Record why specific models were chosen

### Configuration Management

1. **Version Control**: Store configurations in version control
2. **Environment Variables**: Use environment variables for sensitive data
3. **Validation Scripts**: Create scripts to validate configurations
4. **Backup Configurations**: Keep backup configurations for important research

### Performance Optimization

1. **Cache Validation**: Leverage model validation caching
2. **Parallel Processing**: Use parallel validation for multiple models
3. **Resource Monitoring**: Monitor system resources during games
4. **Efficient Presets**: Design presets to minimize redundant operations

### Research Methodology

1. **Control Variables**: Use consistent configurations for fair comparison
2. **Multiple Runs**: Run multiple games for statistical significance
3. **Document Results**: Record detailed results and observations
4. **Reproducible Setup**: Ensure configurations can be reproduced

## Troubleshooting

### Common Issues

#### Model Not Available

```python
# Check model availability
if not model_manager.validate_model("model-name"):
    print("Model not available. Check:")
    print("1. Model name spelling")
    print("2. API key configuration")
    print("3. Network connectivity")
    print("4. Model access permissions")
```

#### Preset Loading Errors

```python
# Validate preset structure
try:
    preset = model_manager.load_preset("preset-name")
except FileNotFoundError:
    print("Preset file not found")
except ValueError as e:
    print(f"Preset validation error: {e}")
```

#### Human Scoring Issues

```python
# Check web interface accessibility
import requests
try:
    response = requests.get("http://127.0.0.1:5001", timeout=5)
    print("Web interface accessible")
except:
    print("Web interface not accessible - check port and firewall")
```

### Debug Mode

Enable debug logging for detailed information:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Run examples with debug output
```

### Getting Help

1. **Review Documentation**: Check configuration guide and troubleshooting guide
2. **Check Examples**: Compare with working example configurations
3. **Validate System**: Run system validation checks
4. **Test Components**: Test individual components in isolation

## Advanced Examples

### Custom Model Integration

```python
# Example of integrating custom model validation
class CustomModelManager(ModelConfigManager):
    def validate_model(self, model_name: str, use_error_handling: bool = True) -> bool:
        if model_name.startswith("custom/"):
            return self._validate_custom_model(model_name)
        return super().validate_model(model_name, use_error_handling)
```

### Performance Monitoring

```python
# Example of performance monitoring during games
import time
import psutil

start_time = time.time()
start_memory = psutil.Process().memory_info().rss

# Run game...

end_time = time.time()
end_memory = psutil.Process().memory_info().rss

print(f"Execution time: {end_time - start_time:.2f}s")
print(f"Memory usage: {(end_memory - start_memory) / 1024 / 1024:.1f}MB")
```

### Batch Processing

```python
# Example of running multiple configurations
configurations = [
    {"name": "config1", "models": ["model1", "model2"]},
    {"name": "config2", "models": ["model3", "model4"]},
    {"name": "config3", "models": ["model5", "model6"]}
]

results = []
for config in configurations:
    print(f"Running configuration: {config['name']}")
    # Create and run game with config
    # Store results
    results.append({"config": config["name"], "result": "success"})

print(f"Completed {len(results)} configurations")
```

## Contributing

### Adding New Examples

1. **Follow Naming Convention**: Use descriptive names with `example_` prefix
2. **Include Documentation**: Add comprehensive comments and docstrings
3. **Error Handling**: Include proper error handling and validation
4. **Test Thoroughly**: Test examples with different configurations

### Example Template

```python
#!/usr/bin/env python3
"""
Example: [Description]

This example demonstrates [functionality].
[Additional description and use cases].

Requirements covered: [requirement numbers]
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Imports...

def main_function():
    """Main function demonstrating the feature"""
    print("=" * 60)
    print("Example Title")
    print("=" * 60)

    try:
        # Implementation...
        print("✅ Example completed successfully!")
        return True
    except Exception as e:
        print(f"❌ Example failed: {e}")
        return False

if __name__ == "__main__":
    success = main_function()
    sys.exit(0 if success else 1)
```

## Resources

- **Configuration Guide**: `docs/CONFIGURATION_GUIDE.md`
- **Troubleshooting Guide**: `docs/TROUBLESHOOTING_GUIDE.md`
- **API Documentation**: Component-specific documentation
- **Test Suite**: `test_comprehensive_suite.py` for validation examples
