# Multi-LLM Debate System Troubleshooting Guide

This guide helps you diagnose and resolve common issues when configuring and running multi-LLM debate games.

## Table of Contents

1. [Model Configuration Issues](#model-configuration-issues)
2. [Preset Management Issues](#preset-management-issues)
3. [Human Scoring Issues](#human-scoring-issues)
4. [Error Handling Issues](#error-handling-issues)
5. [Performance Issues](#performance-issues)
6. [Network and Connectivity Issues](#network-and-connectivity-issues)
7. [Debugging Tools](#debugging-tools)

## Model Configuration Issues

### Issue: Model Validation Fails

**Symptoms:**

- `validate_model()` returns `False`
- Error messages about model not being available
- Game creation fails with invalid model errors

**Common Causes:**

1. **Incorrect Model Name**: Model name doesn't match provider's naming convention
2. **Missing API Keys**: Required API keys not configured
3. **Network Issues**: Cannot reach model provider's API
4. **Model Unavailable**: Model is deprecated or not accessible

**Solutions:**

#### Check Model Name Format

```python
# Correct formats
"deepseek-r1"                    # Direct model name
"openai/gpt-4o"                  # Provider/model format
"anthropic/claude-3-5-sonnet"    # Provider/model format

# Common mistakes
"gpt4o"                          # Missing hyphen
"claude-3.5-sonnet"             # Wrong separator
"openai-gpt-4o"                 # Wrong separator
```

#### Verify API Configuration

```python
# Check if LLMClient is properly configured
from llm_client import LLMClient

llm_client = LLMClient()
try:
    response, reasoning = llm_client.chat(
        [{"role": "user", "content": "Hello"}],
        model="deepseek-r1"
    )
    print("✅ LLMClient working correctly")
except Exception as e:
    print(f"❌ LLMClient error: {e}")
```

#### Test Model Availability

```python
# Test specific models
test_models = [
    "deepseek-r1",
    "openai/gpt-4o-mini",
    "anthropic/claude-3-5-sonnet"
]

for model in test_models:
    try:
        is_valid = model_manager.validate_model(model)
        print(f"{model}: {'✅ Available' if is_valid else '❌ Not available'}")
    except Exception as e:
        print(f"{model}: ❌ Error - {e}")
```

### Issue: Game Creation Fails with Model Errors

**Symptoms:**

- `ValueError` when creating player or judge configurations
- "Invalid models" error messages
- Game initialization fails

**Solutions:**

#### Validate Before Creating Configurations

```python
# Always validate models first
models = ["openai/gpt-4o", "anthropic/claude-3-5-sonnet"]
invalid_models = []

for model in models:
    if not model_manager.validate_model(model):
        invalid_models.append(model)

if invalid_models:
    print(f"❌ Invalid models: {invalid_models}")
    # Use fallback models or update configuration
else:
    # Proceed with game creation
    player_configs = model_manager.create_player_configs(models, names)
```

#### Use Error Handling During Validation

```python
try:
    player_configs = model_manager.create_player_configs(models, names)
except ValueError as e:
    print(f"Configuration error: {e}")
    # Handle the error appropriately
```

## Preset Management Issues

### Issue: Preset Loading Fails

**Symptoms:**

- `FileNotFoundError` when loading presets
- `ValueError` about invalid JSON or missing fields
- Preset validation errors

**Solutions:**

#### Check Preset File Existence

```python
# List available presets
presets = model_manager.list_presets()
print(f"Available presets: {presets}")

# Check if specific preset exists
preset_name = "my_preset"
if preset_name in presets:
    preset = model_manager.load_preset(preset_name)
else:
    print(f"❌ Preset '{preset_name}' not found")
```

#### Validate Preset Structure

```python
# Validate preset before using
try:
    preset = model_manager.load_preset("preset_name")
    print("✅ Preset loaded successfully")
except FileNotFoundError:
    print("❌ Preset file not found")
except ValueError as e:
    print(f"❌ Preset validation error: {e}")
```

#### Fix Common Preset Issues

```python
# Example of a valid preset structure
valid_preset = {
    "preset_name": "example_preset",           # Required
    "description": "Example description",      # Optional but recommended
    "player_configs": [                        # Required
        {"name": "Player1", "model": "model1"},
        {"name": "Player2", "model": "model2"}
    ],
    "judge_configs": [                         # Required
        {"name": "Judge1", "model": "model1"},
        {"name": "Judge2", "model": "model2"}
    ]
}

# Save corrected preset
model_manager.save_preset("corrected_preset", valid_preset)
```

### Issue: Preset Models Not Available

**Symptoms:**

- Preset loads but model validation fails
- Some models in preset are invalid
- Game creation fails after loading preset

**Solutions:**

#### Validate Preset Models

```python
# Check all models in a preset
validation_results = model_manager.validate_preset_models("preset_name")

print("Model validation results:")
for model, is_valid in validation_results.items():
    status = "✅ Valid" if is_valid else "❌ Invalid"
    print(f"  {model}: {status}")

# Check if all models are valid
all_valid = all(validation_results.values())
if not all_valid:
    print("❌ Some models in preset are invalid")
```

#### Update Preset with Valid Models

```python
# Load preset and update invalid models
preset = model_manager.load_preset("preset_name")

# Model replacement mapping
model_replacements = {
    "invalid-model-1": "deepseek-r1",
    "invalid-model-2": "openai/gpt-4o-mini"
}

# Update player configs
for config in preset["player_configs"]:
    if config["model"] in model_replacements:
        old_model = config["model"]
        config["model"] = model_replacements[old_model]
        print(f"Updated {config['name']}: {old_model} → {config['model']}")

# Update judge configs
for config in preset["judge_configs"]:
    if config["model"] in model_replacements:
        old_model = config["model"]
        config["model"] = model_replacements[old_model]
        print(f"Updated {config['name']}: {old_model} → {config['model']}")

# Save updated preset
model_manager.save_preset("updated_preset", preset)
```

## Human Scoring Issues

### Issue: Web Interface Not Accessible

**Symptoms:**

- Cannot access scoring interface URL
- Browser shows connection refused or timeout
- Scoring sessions don't start

**Solutions:**

#### Check Server Status

```python
# Verify server is running
interface = HumanScoringInterface(web_port=5001)

# Check if server started successfully
if hasattr(interface, 'server_running'):
    print(f"Server running: {interface.server_running}")

# Try starting server manually
try:
    interface.start_server()
    print("✅ Server started successfully")
except Exception as e:
    print(f"❌ Server start failed: {e}")
```

#### Check Port Availability

```python
import socket

def check_port(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    return result == 0

port = 5001
if check_port(port):
    print(f"✅ Port {port} is accessible")
else:
    print(f"❌ Port {port} is not accessible")
    print("Try using a different port:")

    # Try alternative ports
    for alt_port in [5002, 5003, 8080, 8081]:
        if not check_port(alt_port):
            print(f"  Port {alt_port} is available")
            break
```

#### Use Alternative Port

```python
# Create interface with different port
interface = HumanScoringInterface(web_port=5002)

# Update game configuration
game = Game(
    player_configs=player_configs,
    judge_configs=judge_configs,
    model_config_manager=model_manager,
    enable_human_scoring=True,
    human_scoring_port=5002  # Use alternative port
)
```

### Issue: Scoring Sessions Timeout

**Symptoms:**

- Scoring sessions expire before completion
- No scores collected despite user input
- Timeout messages in logs

**Solutions:**

#### Increase Timeout Duration

```python
# Start session with longer timeout
interface.start_scoring_session(
    round_info=round_info,
    players=players,
    timeout=600  # 10 minutes instead of default 5
)

# Collect scores with longer timeout
scores = interface.collect_scores(timeout=600)
```

#### Check Session Status

```python
# Monitor session status
session = interface.current_session
if session:
    print(f"Session ID: {session.session_id}")
    print(f"Started: {session.start_time}")
    print(f"Timeout: {session.timeout_seconds}s")
    print(f"Expired: {session.is_expired()}")
    print(f"Complete: {session.is_complete()}")
```

## Error Handling Issues

### Issue: Retry Logic Not Working

**Symptoms:**

- Models fail without retrying
- No fallback models used
- Immediate failures instead of graceful degradation

**Solutions:**

#### Check Error Handler Configuration

```python
# Verify error handler is properly configured
failure_handler = model_manager.get_failure_handler()

print(f"Max retries: {failure_handler.max_retries}")
print(f"Base delay: {failure_handler.base_delay}")

# Check if fallback models are configured
fallback_models = failure_handler.fallback_models
if fallback_models:
    print("Fallback models configured:")
    for primary, fallbacks in fallback_models.items():
        print(f"  {primary} → {fallbacks}")
else:
    print("❌ No fallback models configured")
```

#### Configure Fallback Models

```python
# Set up fallback configuration
fallback_config = {
    "openai/gpt-4o": ["openai/gpt-4o-mini", "deepseek-r1"],
    "anthropic/claude-3-5-sonnet": ["anthropic/claude-3-haiku", "deepseek-r1"],
    "deepseek-r1": ["openai/gpt-4o-mini"]  # Fallback for primary model
}

model_manager.configure_fallback_models(fallback_config)
print("✅ Fallback models configured")
```

#### Test Error Handling

```python
# Test retry logic with invalid model
try:
    content, reasoning = failure_handler.call_with_retry(
        model_name="invalid-model-name",
        messages=[{"role": "user", "content": "Hello"}],
        player_name="TestPlayer"
    )
    print("✅ Fallback worked successfully")
except Exception as e:
    print(f"❌ Error handling failed: {e}")
```

### Issue: Graceful Degradation Not Working

**Symptoms:**

- Games stop completely on model failures
- No degraded responses provided
- Poor error messages for users

**Solutions:**

#### Check Degradation Manager Settings

```python
degradation_manager = model_manager.get_degradation_manager()

# Check configuration
print(f"Default timeout: {degradation_manager.default_timeout}")
print(f"Max failed ratio: {degradation_manager.max_failed_players_ratio}")

# Check current status
status = degradation_manager.get_degradation_status()
print(f"Current status: {status}")
```

#### Test Degradation Scenarios

```python
# Test timeout handling
result = degradation_manager.handle_timeout(
    player_name="TestPlayer",
    model_name="slow-model",
    timeout_duration=30.0
)
print(f"Timeout handling: {result}")

# Test player failure handling
result = degradation_manager.handle_player_model_failure(
    player_name="TestPlayer",
    model_name="failed-model",
    error=Exception("Test error")
)
print(f"Failure handling: {result}")
```

## Performance Issues

### Issue: Slow Model Validation

**Symptoms:**

- Long delays during model validation
- Timeouts during game setup
- Slow preset loading

**Solutions:**

#### Use Validation Caching

```python
# Validation results are cached automatically
# First validation may be slow, subsequent ones are fast

# Check cache status
print(f"Cached models: {list(model_manager._validated_models.keys())}")

# Pre-validate commonly used models
common_models = ["deepseek-r1", "openai/gpt-4o-mini"]
for model in common_models:
    model_manager.validate_model(model)
    print(f"Pre-validated: {model}")
```

#### Parallel Validation

```python
import concurrent.futures

def validate_models_parallel(models):
    """Validate multiple models in parallel"""
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        future_to_model = {
            executor.submit(model_manager.validate_model, model): model
            for model in models
        }

        results = {}
        for future in concurrent.futures.as_completed(future_to_model):
            model = future_to_model[future]
            try:
                results[model] = future.result()
            except Exception as e:
                results[model] = False
                print(f"Error validating {model}: {e}")

        return results

# Use parallel validation for multiple models
models = ["deepseek-r1", "openai/gpt-4o", "anthropic/claude-3-5-sonnet"]
results = validate_models_parallel(models)
print(f"Validation results: {results}")
```

### Issue: High Memory Usage

**Symptoms:**

- Increasing memory usage over time
- System slowdown during long games
- Out of memory errors

**Solutions:**

#### Monitor Resource Usage

```python
import psutil
import os

def check_memory_usage():
    """Check current memory usage"""
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()

    print(f"Memory usage: {memory_info.rss / 1024 / 1024:.1f} MB")
    print(f"Memory percent: {process.memory_percent():.1f}%")

# Check memory before and after operations
check_memory_usage()
# ... perform operations ...
check_memory_usage()
```

#### Clean Up Resources

```python
# Clean up model validation cache periodically
if len(model_manager._validated_models) > 100:
    model_manager._validated_models.clear()
    print("Cleared validation cache")

# Stop unused scoring interfaces
if hasattr(interface, 'stop_server'):
    interface.stop_server()
    print("Stopped scoring interface server")
```

## Network and Connectivity Issues

### Issue: API Connection Failures

**Symptoms:**

- Connection timeout errors
- SSL/TLS certificate errors
- Network unreachable errors

**Solutions:**

#### Check Network Connectivity

```python
import requests

def test_connectivity():
    """Test basic internet connectivity"""
    try:
        response = requests.get("https://httpbin.org/get", timeout=10)
        print(f"✅ Internet connectivity: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ Internet connectivity failed: {e}")
        return False

if not test_connectivity():
    print("Check your internet connection and firewall settings")
```

#### Configure Timeouts

```python
# Increase timeouts for slow connections
degradation_manager = GracefulDegradationManager(
    default_timeout=60.0  # Increase from default 30s
)

# Configure retry delays for network issues
failure_handler = ModelFailureHandler(
    llm_client=llm_client,
    max_retries=5,        # More retries for network issues
    base_delay=2.0,       # Longer base delay
    max_delay=60.0        # Longer max delay
)
```

## Debugging Tools

### Enable Debug Logging

```python
import logging

# Enable debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Enable specific component logging
logger = logging.getLogger('model_config_manager')
logger.setLevel(logging.DEBUG)
```

### Validation Tools

```python
def comprehensive_system_check():
    """Perform comprehensive system validation"""
    print("🔍 Comprehensive System Check")
    print("=" * 50)

    # Check LLMClient
    try:
        llm_client = LLMClient()
        print("✅ LLMClient initialized")
    except Exception as e:
        print(f"❌ LLMClient failed: {e}")
        return False

    # Check ModelConfigManager
    try:
        model_manager = ModelConfigManager(llm_client)
        print("✅ ModelConfigManager initialized")
    except Exception as e:
        print(f"❌ ModelConfigManager failed: {e}")
        return False

    # Check model validation
    test_model = "deepseek-r1"
    try:
        is_valid = model_manager.validate_model(test_model)
        print(f"✅ Model validation: {test_model} is {'valid' if is_valid else 'invalid'}")
    except Exception as e:
        print(f"❌ Model validation failed: {e}")

    # Check preset management
    try:
        presets = model_manager.list_presets()
        print(f"✅ Preset management: {len(presets)} presets available")
    except Exception as e:
        print(f"❌ Preset management failed: {e}")

    # Check human scoring interface
    try:
        interface = HumanScoringInterface(web_port=5999)
        print("✅ HumanScoringInterface initialized")
    except Exception as e:
        print(f"❌ HumanScoringInterface failed: {e}")

    print("✅ System check completed")
    return True

# Run comprehensive check
comprehensive_system_check()
```

### Error Statistics

```python
def print_error_statistics():
    """Print comprehensive error statistics"""
    try:
        error_stats = model_manager.get_error_statistics()

        print("📊 Error Statistics")
        print("=" * 30)

        failure_stats = error_stats.get('failure_statistics', {})
        for key, value in failure_stats.items():
            if value:
                print(f"  {key}: {value}")

        degradation_stats = error_stats.get('degradation_status', {})
        for key, value in degradation_stats.items():
            if value:
                print(f"  {key}: {value}")

    except Exception as e:
        print(f"❌ Could not retrieve error statistics: {e}")

# Print current error statistics
print_error_statistics()
```

## Getting Additional Help

### Log Analysis

1. **Check Console Output**: Look for error messages and warnings
2. **Enable Debug Logging**: Use debug level logging for detailed information
3. **Review Error Statistics**: Check failure and degradation statistics

### Testing Components

1. **Isolate Issues**: Test individual components separately
2. **Use Examples**: Run provided example scripts to verify functionality
3. **Validate Configuration**: Use validation tools to check configurations

### Community Resources

1. **Documentation**: Review configuration guide and examples
2. **Example Scripts**: Check `examples/` directory for reference implementations
3. **Test Suite**: Run test suite to verify system functionality

### Reporting Issues

When reporting issues, include:

1. **Error Messages**: Complete error messages and stack traces
2. **Configuration**: Model names, preset configurations, and settings
3. **Environment**: System information and dependency versions
4. **Steps to Reproduce**: Detailed steps to reproduce the issue
5. **Expected vs Actual**: What you expected vs what actually happened
