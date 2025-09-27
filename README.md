# Multi-LLM Debate Card Game System

A sophisticated framework for running strategic card games between multiple Large Language Models (LLMs), featuring real-time web visualization, comprehensive analytics, and human evaluation capabilities.

## 🎯 What This Project Does

This system enables researchers and developers to:

- **Compare LLM Performance**: Run strategic games between different AI models to analyze their decision-making capabilities
- **Conduct AI Research**: Study how different LLMs approach strategy, bluffing, and social deduction
- **Evaluate Model Behavior**: Use both automated judges and human scoring to assess AI performance
- **Visualize AI Interactions**: Watch games unfold in real-time through a web interface

## 🚀 Quick Start

### Prerequisites

```bash
# Install Python 3.8+
pip install openai flask python-dotenv requests psutil
```

### Setup

1. **Clone and configure**:

```bash
git clone <repository-url>
cd llm-card-game
cp .env.example .env
# Edit .env with your API credentials
```

2. **Run your first game**:

```bash
python examples/example_single_model_game.py
```

3. **View with web interface**:

```bash
cd terminal_stream
python main.py
# Open http://localhost:5000 in your browser
```

## 🏗️ Architecture Overview

### Core Components

- **🎮 Game Engine** (`game.py`): Orchestrates gameplay, manages state, and coordinates between players and judges
- **🤖 Player System** (`player.py`): LLM-powered agents that make strategic decisions, challenge opponents, and adapt strategies
- **⚖️ Judge Panel** (`judge_panel.py`): Multiple LLM judges that evaluate player performance and maintain fair scoring
- **📊 Analytics** (`model_performance_analytics.py`): Comprehensive performance tracking and statistical analysis
- **🌐 Web Interface** (`terminal_stream/`): Real-time game visualization with streaming updates
- **👥 Human Scoring** (`human_scoring_interface.py`): Web-based interface for human evaluation and comparison

## 📁 Project Structure

```
llm-card-game/
├── 🎮 Core Game Engine
│   ├── game.py                    # Main game orchestration and flow control
│   ├── player.py                  # LLM player agents with strategic AI
│   ├── judge_panel.py             # Multi-judge evaluation system
│   └── game_record.py             # Comprehensive game state tracking
│
├── 🤖 LLM Integration
│   ├── llm_client.py              # Universal LLM API client
│   ├── model_config_manager.py    # Model validation and configuration
│   └── error_handling.py          # Robust error handling and fallbacks
│
├── 📊 Analytics & Scoring
│   ├── model_performance_analytics.py  # Performance metrics and analysis
│   ├── game_analytics_integration.py   # Game event analytics
│   ├── human_scoring_interface.py      # Web-based human evaluation
│   └── player_matchup_analyze.py       # Head-to-head analysis
│
├── 🌐 Web Interface
│   └── terminal_stream/
│       ├── main.py                # Flask server with real-time streaming
│       ├── stream_handler.py      # Output capture and streaming
│       ├── game_runner.py         # Web-integrated game execution
│       └── index.html             # Real-time game visualization
│
├── 🎯 Prompts & Rules
│   └── prompt/
│       ├── rule_base.txt          # Core game rules and mechanics
│       ├── play_card_prompt_template.txt    # Strategic decision prompts
│       ├── challenge_prompt_template.txt   # Challenge evaluation prompts
│       ├── judge_prompt_template.txt       # Judge scoring prompts
│       └── reflect_prompt_template.txt     # Post-game reflection prompts
│
├── 📋 Configuration & Presets
│   └── model_presets/             # Pre-configured model combinations
│       ├── gpt_vs_claude.json     # Provider comparison setup
│       ├── mixed_models_example.json  # Multi-model research setup
│       ├── research_diverse.json  # Diverse model research configuration
│       └── single_*.json          # Single-model baseline configurations
│
├── 📚 Examples & Documentation
│   ├── examples/                  # Comprehensive usage examples
│   │   ├── example_single_model_game.py    # Baseline testing
│   │   ├── example_mixed_model_game.py     # Multi-model comparison
│   │   └── example_human_scoring_game.py   # Human evaluation integration
│   └── docs/                      # Detailed documentation
│       ├── CONFIGURATION_GUIDE.md # Setup and configuration guide
│       ├── TROUBLESHOOTING_GUIDE.md # Common issues and solutions
│       └── game_architecture.md   # Technical architecture details
│
└── 🧪 Testing & Validation
    ├── test_comprehensive_suite.py    # Full system integration tests
    ├── test_model_integration.py      # LLM integration tests
    ├── test_multi_model_integration.py # Multi-model scenario tests
    └── validate_task_completion.py    # Task validation utilities
```

## 🎯 Key Features

### 🤖 Multi-Model Support

- **Universal LLM Integration**: Works with OpenAI, Anthropic, DeepSeek, and other providers
- **Model Validation**: Automatic validation of model availability and configuration
- **Fallback Systems**: Graceful degradation when models are unavailable
- **Performance Analytics**: Detailed metrics comparing model performance

### 🎮 Advanced Game Mechanics

- **Strategic Decision Making**: Players must balance risk, deception, and resource management
- **Social Deduction**: Bluffing and challenge mechanics test AI reasoning capabilities
- **Multi-Judge Evaluation**: Multiple AI judges provide balanced, fair scoring
- **Adaptive Strategies**: Players learn and adapt based on opponent behavior

### 📊 Comprehensive Analytics

- **Real-time Performance Tracking**: Monitor model performance during games
- **Statistical Analysis**: Win rates, decision patterns, and strategic preferences
- **Comparative Studies**: Head-to-head analysis between different models
- **Human vs AI Evaluation**: Compare human and AI assessment of performance

### 🌐 Real-Time Visualization

- **Live Game Streaming**: Watch games unfold in real-time through web interface
- **Interactive Dashboards**: Monitor player status, scores, and game progression
- **Multi-language Support**: Handles Chinese text and special characters
- **Mobile-Friendly**: Responsive design works on desktop and mobile devices

## 🚀 Usage Examples

- **Output Persistence**: Game output is not persisted; closing browser clears display
- **Default Port**: Uses port 5000 (configurable)
- **Requirements**: Python 3.8+ and Flask

## 📋 Configuration

### Environment Setup

```bash
# Copy example environment file
cp .env.example .env

# Edit with your API credentials
API_BASE_URL=https://api.openai.com/v1  # or your provider's URL
API_KEY=your_api_key_here
```

### Model Configuration

```python
# Available model formats
models = [
    "deepseek-r1",                    # Direct model name
    "openai/gpt-4o",                  # Provider/model format
    "anthropic/claude-3-5-sonnet",    # Cross-provider support
    "google/gemini-pro"               # Multiple providers
]
```

### Preset Management

```python
# Create custom preset
preset = {
    "preset_name": "research_setup",
    "description": "Custom research configuration",
    "player_configs": [...],
    "judge_configs": [...]
}
model_manager.save_preset("research_setup", preset)

# Use existing presets
available_presets = model_manager.list_presets()
preset = model_manager.load_preset("gpt_vs_claude")
```

## 🔧 Advanced Features

### Human Scoring Integration

```python
# Enable human evaluation alongside AI judges
game = Game(
    player_configs,
    judge_configs,
    model_manager,
    enable_human_scoring=True,
    human_scoring_port=5001
)

# Access scoring interface at http://localhost:5001
```

### Performance Analytics

```python
# Enable comprehensive analytics
game = Game(
    player_configs,
    judge_configs,
    model_manager,
    enable_analytics=True
)

# Access analytics after game completion
analytics = game.get_analytics()
print(f"Win rates: {analytics.win_rates}")
print(f"Decision patterns: {analytics.decision_patterns}")
```

### Error Handling & Fallbacks

```python
# Configure fallback models for reliability
fallback_config = {
    "openai/gpt-4o": ["openai/gpt-4o-mini", "deepseek-r1"],
    "anthropic/claude-3-5-sonnet": ["anthropic/claude-3-haiku"]
}
model_manager.configure_fallback_models(fallback_config)
```

### Batch Processing

```python
# Run multiple games for statistical analysis
from multi_game_runner import MultiGameRunner

runner = MultiGameRunner()
results = runner.run_batch([
    "single_gpt4o",
    "gpt_vs_claude",
    "mixed_models_example"
], num_games=10)
```

## 🐛 Debugging & Troubleshooting

### Debug Mode

```python
# Enable detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Player-specific debugging (uncomment in player.py)
# DEBUG OUTPUT section in choose_cards_to_play method
```

### Common Issues

#### Model Validation Failures

```python
# Check model availability
if not model_manager.validate_model("your-model"):
    print("Model validation failed. Check:")
    print("1. Model name spelling")
    print("2. API key configuration")
    print("3. Network connectivity")
    print("4. Provider access permissions")
```

#### Web Interface Issues

```bash
# Check port availability
lsof -i :5000

# Test web interface
curl http://localhost:5000/health
```

#### Performance Issues

```python
# Monitor resource usage
import psutil
print(f"Memory: {psutil.virtual_memory().percent}%")
print(f"CPU: {psutil.cpu_percent()}%")
```

## 📚 Documentation

- **📖 [Configuration Guide](docs/CONFIGURATION_GUIDE.md)**: Detailed setup instructions
- **🔧 [Troubleshooting Guide](docs/TROUBLESHOOTING_GUIDE.md)**: Common issues and solutions
- **🏗️ [Architecture Guide](docs/game_architecture.md)**: Technical implementation details
- **📋 [Examples](examples/README.md)**: Comprehensive usage examples

## 🧪 Testing

```bash
# Run comprehensive test suite
python test_comprehensive_suite.py

# Test specific components
python test_model_integration.py
python test_multi_model_integration.py

# Validate task completion
python validate_task_completion.py
```

## 📦 Installation

### Requirements

- **Python**: 3.8 or higher
- **Dependencies**: `pip install -r requirements.txt`
- **API Access**: LLM provider API keys (OpenAI, Anthropic, etc.)

### Quick Install

```bash
git clone <repository-url>
cd llm-card-game
pip install openai flask python-dotenv requests psutil
cp .env.example .env
# Edit .env with your credentials
python examples/example_single_model_game.py
```

## 🤝 Contributing

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Add tests**: Ensure new features have comprehensive tests
4. **Update documentation**: Keep README and docs current
5. **Submit pull request**: Include detailed description of changes

## 📄 License

This project is licensed under the terms specified in the [LICENSE](LICENSE) file.

---

## 🎯 Use Cases

### 🔬 AI Research

- **Model Comparison Studies**: Compare reasoning capabilities across different LLMs
- **Strategic Behavior Analysis**: Study how AI approaches deception and social dynamics
- **Performance Benchmarking**: Establish baselines for AI decision-making quality

### 🎓 Educational Applications

- **AI Demonstration**: Show students how different AI models think and strategize
- **Game Theory Research**: Explore strategic interactions in controlled environments
- **Human-AI Comparison**: Compare human and AI approaches to strategic problems

### 🏢 Commercial Applications

- **Model Selection**: Evaluate which LLMs work best for your specific use cases
- **Quality Assurance**: Test AI behavior before deploying in production
- **Competitive Analysis**: Compare your AI against industry-standard models

## License

See the LICENSE file for details.
