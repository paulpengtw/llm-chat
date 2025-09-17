# Design Document

## Overview

The multi-LLM debate feature extends the existing card game architecture to support different LLM models competing against each other. The design maintains the current game mechanics while adding model diversity, human scoring capabilities, and enhanced observability. The system will support up to 4 different LLM models for players and judges, with configuration presets and human evaluation interfaces.

## Architecture

### Current Architecture Analysis

The existing system follows a clean separation of concerns:
- `Game` class orchestrates game flow and player interactions
- `Player` class handles individual LLM decision-making via `LLMClient`
- `JudgePanel` class manages AI judge evaluations
- `GameRecord` class tracks all game events and decisions
- `LLMClient` class provides unified API access to different models

### Enhanced Architecture

The multi-LLM enhancement preserves this architecture while adding:
- **Model Configuration Management**: Centralized handling of model assignments and validation
- **Human Scoring Interface**: Web-based interface for human judges to score LLM performance
- **Model Performance Tracking**: Enhanced analytics for model-specific behavior analysis
- **Configuration Presets**: Pre-defined model combinations for common research scenarios

## Components and Interfaces

### 1. Model Configuration Manager

**Purpose**: Centralize model configuration, validation, and preset management

**Interface**:
```python
class ModelConfigManager:
    def __init__(self, llm_client: LLMClient)
    def validate_model(self, model_name: str) -> bool
    def load_preset(self, preset_name: str) -> Dict
    def save_preset(self, preset_name: str, config: Dict) -> None
    def get_available_models(self) -> List[str]
    def create_player_configs(self, models: List[str], names: List[str]) -> List[Dict]
    def create_judge_configs(self, models: List[str], names: List[str]) -> List[Dict]
```

**Responsibilities**:
- Validate model availability through LLM client
- Manage configuration presets (stored as JSON files)
- Generate player and judge configurations
- Provide model discovery and validation

### 2. Human Scoring Interface

**Purpose**: Allow human judges to score LLM performance each round

**Interface**:
```python
class HumanScoringInterface:
    def __init__(self, web_port: int = 5001)
    def start_scoring_session(self, round_info: Dict, players: List[str]) -> None
    def collect_scores(self, timeout: int = 300) -> Dict[str, Dict[str, int]]
    def display_round_summary(self, round_info: Dict, ai_votes: Dict, human_scores: Dict) -> None
    def get_scoring_statistics(self) -> Dict
```

**Web Interface Components**:
- Round information display showing player actions and behaviors
- Scoring forms with 0-5 scales for multiple criteria
- Real-time score collection and validation
- Summary displays comparing AI vs human evaluations

### 3. Enhanced Game Record

**Purpose**: Track model-specific performance and human scoring data

**New Fields**:
```python
@dataclass
class ModelPerformanceRecord:
    model_name: str
    player_name: str
    decision_count: int
    successful_challenges: int
    failed_challenges: int
    average_response_time: float
    human_scores: List[Dict[str, int]]

@dataclass 
class RoundRecord:
    # ... existing fields ...
    human_scores: Dict[str, Dict[str, int]] = field(default_factory=dict)
    model_assignments: Dict[str, str] = field(default_factory=dict)
```

### 4. Enhanced Judge Panel

**Purpose**: Integrate human scoring with existing AI judge system

**Enhanced Interface**:
```python
class JudgePanel:
    def __init__(self, judge_configs: List[Dict], enable_human_scoring: bool = False)
    def set_human_scoring_interface(self, interface: HumanScoringInterface) -> None
    def evaluate_round_with_human_input(self, round_info: Dict) -> Dict
    def get_combined_evaluation_summary(self) -> str
```

## Data Models

### Configuration Schema

```python
# Model preset configuration
{
    "preset_name": "gpt_vs_claude",
    "description": "GPT-4 models vs Claude models",
    "player_configs": [
        {"name": "GPT-Alpha", "model": "openai/gpt-4o"},
        {"name": "GPT-Beta", "model": "openai/gpt-4o-mini"},
        {"name": "Claude-Alpha", "model": "anthropic/claude-3-sonnet"},
        {"name": "Claude-Beta", "model": "anthropic/claude-3-haiku"}
    ],
    "judge_configs": [
        {"name": "Justice", "model": "openai/gpt-4o"},
        {"name": "Wisdom", "model": "anthropic/claude-3-sonnet"},
        {"name": "Truth", "model": "openai/gpt-4o-mini"},
        {"name": "Honor", "model": "anthropic/claude-3-haiku"}
    ]
}
```

### Human Scoring Schema

```python
# Human scoring data structure
{
    "round_id": 1,
    "scorer_id": "human_judge_1",
    "scores": {
        "GPT-Alpha": {
            "strategic_thinking": 4,
            "bluffing_skill": 3,
            "reasoning_quality": 5,
            "overall_performance": 4
        },
        "Claude-Beta": {
            "strategic_thinking": 3,
            "bluffing_skill": 5,
            "reasoning_quality": 4,
            "overall_performance": 4
        }
    },
    "comments": "GPT-Alpha showed excellent logical reasoning but predictable bluffing patterns"
}
```

## Error Handling

### Model Failure Recovery

1. **Retry Logic**: Implement exponential backoff for temporary API failures
2. **Fallback Models**: Allow configuration of backup models for each position
3. **Graceful Degradation**: Continue games with reduced functionality if models fail
4. **Error Logging**: Comprehensive logging for debugging model-specific issues

### Validation Strategy

1. **Pre-game Validation**: Test all configured models before game start
2. **Runtime Validation**: Validate model responses and implement fallbacks
3. **Configuration Validation**: Ensure all required models are available
4. **Human Input Validation**: Validate scoring inputs and handle timeouts

## Testing Strategy

### Unit Testing

1. **Model Configuration Manager**: Test preset loading, model validation, configuration generation
2. **Human Scoring Interface**: Test score collection, validation, timeout handling
3. **Enhanced Game Components**: Test model assignment tracking, performance recording
4. **Error Handling**: Test failure scenarios and recovery mechanisms

### Integration Testing

1. **Multi-Model Games**: Test games with different model combinations
2. **Human Scoring Integration**: Test combined AI and human evaluation workflows
3. **Web Interface Integration**: Test real-time scoring during live games
4. **Performance Tracking**: Test analytics and reporting functionality

### System Testing

1. **End-to-End Scenarios**: Complete games with mixed models and human scoring
2. **Performance Testing**: Test system behavior under model latency variations
3. **Failure Recovery Testing**: Test graceful handling of model failures
4. **User Experience Testing**: Test human judge interface usability

## Implementation Considerations

### Backward Compatibility

- All existing game configurations must continue to work unchanged
- Current game record formats must remain compatible
- Existing web interface functionality must be preserved
- Command-line usage patterns must remain the same

### Performance Optimization

- Parallel model calls where possible to reduce latency
- Efficient caching of model validation results
- Optimized web interface for real-time scoring
- Minimal overhead for model tracking and analytics

### Security Considerations

- Validate all model names to prevent injection attacks
- Secure human scoring interface against manipulation
- Protect configuration files from unauthorized access
- Implement rate limiting for model API calls

### Scalability

- Support for adding new model providers without code changes
- Configurable timeout and retry parameters
- Efficient storage of performance analytics
- Modular design for easy feature extension