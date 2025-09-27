"""
Error Handling and Recovery System for Multi-LLM Debate Game

This module provides comprehensive error handling, retry logic, and graceful
degradation strategies for model failures and API issues.
"""

import time
import logging
import random
import signal
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
try:
    from llm_client import LLMClient
except ImportError:
    # For testing without dependencies
    LLMClient = None


class ErrorType(Enum):
    """Types of errors that can occur in the system"""
    MODEL_API_FAILURE = "model_api_failure"
    MODEL_TIMEOUT = "model_timeout"
    MODEL_UNAVAILABLE = "model_unavailable"
    INVALID_RESPONSE = "invalid_response"
    CONFIGURATION_ERROR = "configuration_error"
    NETWORK_ERROR = "network_error"


@dataclass
class ErrorContext:
    """Context information for error handling"""
    error_type: ErrorType
    model_name: str
    player_name: Optional[str] = None
    attempt_count: int = 0
    original_error: Optional[Exception] = None
    timestamp: float = 0.0
    
    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()


class ModelFailureHandler:
    """
    Handles model failures with retry logic, exponential backoff, and fallback strategies.
    
    This class provides:
    - Exponential backoff retry logic for temporary failures
    - Fallback model configuration and automatic switching
    - Comprehensive error logging for debugging
    - Graceful degradation strategies
    """
    
    def __init__(self, llm_client, max_retries: int = 3, 
                 base_delay: float = 1.0, max_delay: float = 30.0):
        """
        Initialize the failure handler.
        
        Args:
            llm_client: LLMClient instance for making API calls (or None for testing)
            max_retries: Maximum number of retry attempts
            base_delay: Base delay for exponential backoff (seconds)
            max_delay: Maximum delay between retries (seconds)
        """
        self.llm_client = llm_client
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        
        # Track failure counts per model
        self.failure_counts: Dict[str, int] = {}
        self.consecutive_failures: Dict[str, int] = {}
        self.last_success_time: Dict[str, float] = {}
        
        # Fallback model configurations
        self.fallback_models: Dict[str, List[str]] = {}
        
        # Configure logging
        self.logger = self._setup_logging()
    
    def _setup_logging(self) -> logging.Logger:
        """Set up error logging configuration"""
        logger = logging.getLogger('model_failure_handler')
        logger.setLevel(logging.INFO)
        
        # Create file handler if it doesn't exist
        if not logger.handlers:
            handler = logging.FileHandler('model_errors.log')
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
            # Also log to console for immediate feedback
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        return logger
    
    def set_fallback_models(self, model_fallbacks: Dict[str, List[str]]) -> None:
        """
        Set fallback model configurations.
        
        Args:
            model_fallbacks: Dictionary mapping primary models to fallback model lists
                           e.g., {"gpt-4o": ["gpt-4o-mini", "deepseek-r1"]}
        """
        self.fallback_models = model_fallbacks.copy()
        self.logger.info(f"Configured fallback models: {model_fallbacks}")
    
    def _calculate_delay(self, attempt: int) -> float:
        """Calculate exponential backoff delay with jitter"""
        delay = min(self.base_delay * (2 ** attempt), self.max_delay)
        # Add jitter to prevent thundering herd
        jitter = random.uniform(0.1, 0.3) * delay
        return delay + jitter
    
    def _classify_error(self, error: Exception, model_name: str) -> ErrorType:
        """Classify the type of error for appropriate handling"""
        error_str = str(error).lower()
        
        if "timeout" in error_str or "timed out" in error_str:
            return ErrorType.MODEL_TIMEOUT
        elif "rate limit" in error_str or "429" in error_str:
            return ErrorType.MODEL_API_FAILURE
        elif "invalid model" in error_str or "not found" in error_str:
            return ErrorType.MODEL_UNAVAILABLE
        elif "network" in error_str or "connection" in error_str:
            return ErrorType.NETWORK_ERROR
        elif "json" in error_str or "parse" in error_str:
            return ErrorType.INVALID_RESPONSE
        else:
            return ErrorType.MODEL_API_FAILURE
    
    def _should_retry(self, error_context: ErrorContext) -> bool:
        """Determine if an error should be retried"""
        # Don't retry configuration errors or model unavailable errors
        if error_context.error_type in [ErrorType.CONFIGURATION_ERROR, ErrorType.MODEL_UNAVAILABLE]:
            return False
        
        # Don't retry if we've exceeded max attempts
        if error_context.attempt_count >= self.max_retries:
            return False
        
        # Check if model has too many consecutive failures
        consecutive = self.consecutive_failures.get(error_context.model_name, 0)
        if consecutive >= self.max_retries * 2:  # Allow more failures before giving up completely
            return False
        
        return True
    
    def _get_fallback_model(self, failed_model: str) -> Optional[str]:
        """Get the next available fallback model"""
        if failed_model not in self.fallback_models:
            return None
        
        fallbacks = self.fallback_models[failed_model]
        
        # Try each fallback in order, skipping ones that have also failed recently
        for fallback in fallbacks:
            consecutive_failures = self.consecutive_failures.get(fallback, 0)
            if consecutive_failures < self.max_retries:
                return fallback
        
        return None
    
    def _record_success(self, model_name: str) -> None:
        """Record successful model interaction"""
        self.consecutive_failures[model_name] = 0
        self.last_success_time[model_name] = time.time()
    
    def _record_failure(self, error_context: ErrorContext) -> None:
        """Record model failure for tracking"""
        model_name = error_context.model_name
        
        # Update failure counts
        self.failure_counts[model_name] = self.failure_counts.get(model_name, 0) + 1
        self.consecutive_failures[model_name] = self.consecutive_failures.get(model_name, 0) + 1
        
        # Log the failure
        self.logger.error(
            f"Model failure - Model: {model_name}, Player: {error_context.player_name}, "
            f"Error Type: {error_context.error_type.value}, Attempt: {error_context.attempt_count}, "
            f"Error: {error_context.original_error}"
        )
    
    def call_with_retry(self, model_name: str, messages: List[Dict], 
                       player_name: Optional[str] = None, timeout: Optional[float] = None) -> Tuple[str, str]:
        """
        Make LLM API call with retry logic and fallback handling.
        
        Args:
            model_name: Name of the model to use
            messages: Messages to send to the model
            player_name: Name of the player making the request (for logging)
            timeout: Optional timeout for the API call (seconds)
            
        Returns:
            Tuple[str, str]: (content, reasoning_content) from successful API call
            
        Raises:
            ModelFailureException: If all retry attempts and fallbacks fail
        """
        current_model = model_name
        attempt = 0
        
        while attempt <= self.max_retries:
            try:
                # Make the API call with timeout if specified
                if timeout:
                    content, reasoning = self._call_with_timeout(messages, current_model, timeout)
                else:
                    content, reasoning = self.llm_client.chat(messages, model=current_model)
                
                # Check if we got a valid response
                if content.strip():
                    self._record_success(current_model)
                    
                    # Log successful fallback usage
                    if current_model != model_name:
                        self.logger.info(
                            f"Successful fallback - Original: {model_name}, "
                            f"Used: {current_model}, Player: {player_name}"
                        )
                    
                    return content, reasoning
                else:
                    # Empty response is treated as an error
                    raise ValueError("Empty response from model")
                    
            except Exception as e:
                error_context = ErrorContext(
                    error_type=self._classify_error(e, current_model),
                    model_name=current_model,
                    player_name=player_name,
                    attempt_count=attempt,
                    original_error=e
                )
                
                self._record_failure(error_context)
                
                # Check if we should retry with the same model
                if self._should_retry(error_context):
                    delay = self._calculate_delay(attempt)
                    self.logger.warning(
                        f"Retrying in {delay:.1f}s - Model: {current_model}, "
                        f"Player: {player_name}, Attempt: {attempt + 1}/{self.max_retries}"
                    )
                    time.sleep(delay)
                    attempt += 1
                    continue
                
                # Try fallback model if available
                fallback_model = self._get_fallback_model(model_name)
                if fallback_model and current_model == model_name:
                    self.logger.warning(
                        f"Switching to fallback model - Original: {model_name}, "
                        f"Fallback: {fallback_model}, Player: {player_name}"
                    )
                    current_model = fallback_model
                    attempt = 0  # Reset attempt counter for fallback
                    continue
                
                # All options exhausted
                raise ModelFailureException(
                    f"All retry attempts failed for model {model_name} "
                    f"(player: {player_name}). Last error: {str(e)}"
                ) from e
        
        # This should not be reached, but just in case
        raise ModelFailureException(
            f"Unexpected failure in retry logic for model {model_name}"
        )
    
    def _call_with_timeout(self, messages: List[Dict], model_name: str, timeout: float) -> Tuple[str, str]:
        """
        Make LLM API call with timeout handling.
        
        Args:
            messages: Messages to send to the model
            model_name: Name of the model to use
            timeout: Timeout in seconds
            
        Returns:
            Tuple[str, str]: (content, reasoning_content) from API call
            
        Raises:
            TimeoutError: If the call times out
        """
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(self.llm_client.chat, messages, model_name)
            try:
                return future.result(timeout=timeout)
            except FutureTimeoutError:
                # Cancel the future if possible
                future.cancel()
                raise TimeoutError(f"Model {model_name} timed out after {timeout} seconds")
    
    def get_failure_statistics(self) -> Dict[str, Any]:
        """Get failure statistics for monitoring and debugging"""
        return {
            "failure_counts": self.failure_counts.copy(),
            "consecutive_failures": self.consecutive_failures.copy(),
            "last_success_times": self.last_success_time.copy(),
            "configured_fallbacks": self.fallback_models.copy()
        }
    
    def reset_failure_counts(self, model_name: Optional[str] = None) -> None:
        """Reset failure counts for a specific model or all models"""
        if model_name:
            self.consecutive_failures[model_name] = 0
            self.logger.info(f"Reset failure count for model: {model_name}")
        else:
            self.consecutive_failures.clear()
            self.logger.info("Reset all failure counts")


class ModelFailureException(Exception):
    """Exception raised when all model retry attempts and fallbacks fail"""
    pass


class GracefulDegradationManager:
    """
    Manages graceful degradation strategies when models fail.
    
    This class provides:
    - Logic to continue games when individual models fail
    - Timeout handling for slow model responses
    - User-friendly error messages for model configuration issues
    """
    
    def __init__(self, default_timeout: float = 60.0, max_timeout_count: int = 3):
        """
        Initialize the degradation manager.
        
        Args:
            default_timeout: Default timeout for model responses (seconds)
            max_timeout_count: Maximum timeouts before treating as model failure
        """
        self.default_timeout = default_timeout
        self.max_timeout_count = max_timeout_count
        self.logger = logging.getLogger('graceful_degradation')
        
        # Track degraded players and their fallback strategies
        self.degraded_players: Dict[str, str] = {}  # player_name -> reason
        self.timeout_counts: Dict[str, int] = {}
        self.model_performance: Dict[str, Dict[str, Any]] = {}  # Track model performance metrics
        
        # Configure logging if not already done
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def handle_player_model_failure(self, player_name: str, model_name: str, 
                                  error: Exception) -> Dict[str, Any]:
        """
        Handle a player's model failure with graceful degradation.
        
        Args:
            player_name: Name of the player whose model failed
            model_name: Name of the failed model
            error: The original error that occurred
            
        Returns:
            Dict containing degradation strategy and fallback response
        """
        self.logger.warning(
            f"Handling model failure for player {player_name} (model: {model_name}): {error}"
        )
        
        # Mark player as degraded
        self.degraded_players[player_name] = f"Model {model_name} failed: {str(error)}"
        
        # Provide fallback response based on the context
        fallback_response = self._generate_fallback_response(player_name, model_name)
        
        return {
            "success": True,
            "degraded": True,
            "player_name": player_name,
            "fallback_response": fallback_response,
            "reason": str(error)
        }
    
    def _generate_fallback_response(self, player_name: str, model_name: str) -> Dict[str, Any]:
        """Generate a reasonable fallback response when a model fails"""
        # For card playing decisions, provide a conservative fallback
        fallback_play_response = {
            "played_cards": ["K"],  # Play one safe card
            "behavior": "conservative",
            "talk": f"I'm having technical difficulties, playing conservatively.",
            "play_reason": f"Model {model_name} unavailable, using fallback strategy"
        }
        
        # For challenge decisions, default to not challenging (safer option)
        fallback_challenge_response = {
            "was_challenged": False,
            "challenge_reason": f"Model {model_name} unavailable, defaulting to no challenge"
        }
        
        return {
            "play_response": fallback_play_response,
            "challenge_response": fallback_challenge_response
        }
    
    def handle_timeout(self, player_name: str, model_name: str, 
                      timeout_duration: float) -> Dict[str, Any]:
        """
        Handle model timeout with appropriate fallback.
        
        Args:
            player_name: Name of the player whose model timed out
            model_name: Name of the model that timed out
            timeout_duration: How long the timeout lasted
            
        Returns:
            Dict containing timeout handling result
        """
        self.timeout_counts[player_name] = self.timeout_counts.get(player_name, 0) + 1
        
        # Update model performance tracking
        self._update_model_performance(model_name, "timeout", timeout_duration)
        
        self.logger.warning(
            f"Model timeout for player {player_name} (model: {model_name}) "
            f"after {timeout_duration:.1f}s. Timeout count: {self.timeout_counts[player_name]}"
        )
        
        # Display user-friendly message
        user_message = self.generate_user_friendly_error(
            ErrorType.MODEL_TIMEOUT, model_name, player_name
        )
        print(f"⏰ {user_message}")
        
        # If too many timeouts, treat as model failure
        if self.timeout_counts[player_name] >= self.max_timeout_count:
            self.logger.error(
                f"Player {player_name} exceeded maximum timeout count ({self.max_timeout_count}), "
                f"treating as model failure"
            )
            failure_result = self.handle_player_model_failure(
                player_name, model_name, 
                TimeoutError(f"Model timed out {self.timeout_counts[player_name]} times")
            )
            # Add timeout count to the failure result
            failure_result["timeout_count"] = self.timeout_counts[player_name]
            return failure_result
        
        # Otherwise, provide timeout-specific fallback
        fallback_response = self._generate_fallback_response(player_name, model_name)
        
        return {
            "success": True,
            "timeout": True,
            "player_name": player_name,
            "fallback_response": fallback_response,
            "timeout_count": self.timeout_counts[player_name],
            "user_message": user_message
        }
    
    def is_player_degraded(self, player_name: str) -> bool:
        """Check if a player is currently in degraded mode"""
        return player_name in self.degraded_players
    
    def get_degradation_status(self) -> Dict[str, Any]:
        """Get current degradation status for all players"""
        return {
            "degraded_players": self.degraded_players.copy(),
            "timeout_counts": self.timeout_counts.copy()
        }
    
    def reset_player_status(self, player_name: str) -> None:
        """Reset a player's degradation status"""
        if player_name in self.degraded_players:
            del self.degraded_players[player_name]
        if player_name in self.timeout_counts:
            del self.timeout_counts[player_name]
        
        self.logger.info(f"Reset degradation status for player: {player_name}")
    
    def _update_model_performance(self, model_name: str, event_type: str, 
                                 duration: Optional[float] = None) -> None:
        """Update model performance tracking"""
        if model_name not in self.model_performance:
            self.model_performance[model_name] = {
                "total_calls": 0,
                "successful_calls": 0,
                "timeouts": 0,
                "failures": 0,
                "total_response_time": 0.0,
                "average_response_time": 0.0
            }
        
        stats = self.model_performance[model_name]
        stats["total_calls"] += 1
        
        if event_type == "success":
            stats["successful_calls"] += 1
            if duration:
                stats["total_response_time"] += duration
                stats["average_response_time"] = stats["total_response_time"] / stats["successful_calls"]
        elif event_type == "timeout":
            stats["timeouts"] += 1
        elif event_type == "failure":
            stats["failures"] += 1
    
    def get_model_performance_report(self) -> Dict[str, Any]:
        """Get detailed model performance report"""
        report = {}
        for model_name, stats in self.model_performance.items():
            total_calls = stats["total_calls"]
            if total_calls > 0:
                success_rate = (stats["successful_calls"] / total_calls) * 100
                timeout_rate = (stats["timeouts"] / total_calls) * 100
                failure_rate = (stats["failures"] / total_calls) * 100
                
                report[model_name] = {
                    "total_calls": total_calls,
                    "success_rate": f"{success_rate:.1f}%",
                    "timeout_rate": f"{timeout_rate:.1f}%",
                    "failure_rate": f"{failure_rate:.1f}%",
                    "average_response_time": f"{stats['average_response_time']:.2f}s"
                }
        
        return report
    
    def should_continue_game(self, failed_players: List[str], total_players: int) -> bool:
        """
        Determine if the game should continue based on failed players.
        
        Args:
            failed_players: List of player names that have failed
            total_players: Total number of players in the game
            
        Returns:
            bool: True if game should continue, False if too many failures
        """
        failure_threshold = 0.5  # Continue if less than 50% of players have failed
        failure_rate = len(failed_players) / total_players
        
        should_continue = failure_rate < failure_threshold
        
        if not should_continue:
            self.logger.warning(
                f"Game continuation check failed: {len(failed_players)}/{total_players} "
                f"players have failed ({failure_rate:.1%} failure rate)"
            )
        
        return should_continue
    
    def generate_game_continuation_message(self, degraded_players: List[str]) -> str:
        """Generate message about game continuation with degraded players"""
        if not degraded_players:
            return "All players are operating normally."
        
        if len(degraded_players) == 1:
            return (
                f"Player {degraded_players[0]} is using fallback strategies due to model issues, "
                f"but the game continues normally."
            )
        else:
            player_list = ", ".join(degraded_players[:-1]) + f" and {degraded_players[-1]}"
            return (
                f"Players {player_list} are using fallback strategies due to model issues, "
                f"but the game continues with reduced AI capabilities for these players."
            )
    
    def generate_user_friendly_error(self, error_type: ErrorType, 
                                   model_name: str, player_name: str = None) -> str:
        """Generate user-friendly error messages for different error types"""
        messages = {
            ErrorType.MODEL_API_FAILURE: (
                f"The AI model '{model_name}' is experiencing technical difficulties. "
                f"{'Player ' + player_name + ' will' if player_name else 'The system will'} "
                f"use a backup strategy to continue the game."
            ),
            ErrorType.MODEL_TIMEOUT: (
                f"The AI model '{model_name}' is responding slowly. "
                f"{'Player ' + player_name + ' will' if player_name else 'The system will'} "
                f"use a quicker fallback response to keep the game moving."
            ),
            ErrorType.MODEL_UNAVAILABLE: (
                f"The AI model '{model_name}' is currently unavailable. "
                f"Please check your model configuration or try a different model."
            ),
            ErrorType.INVALID_RESPONSE: (
                f"The AI model '{model_name}' provided an unexpected response format. "
                f"{'Player ' + player_name + ' will' if player_name else 'The system will'} "
                f"use a standard fallback response."
            ),
            ErrorType.CONFIGURATION_ERROR: (
                f"There's a configuration issue with model '{model_name}'. "
                f"Please check your model settings and try again."
            ),
            ErrorType.NETWORK_ERROR: (
                f"Network connectivity issues are affecting model '{model_name}'. "
                f"The game will attempt to continue with backup strategies."
            )
        }
        
        return messages.get(error_type, f"An unexpected error occurred with model '{model_name}'.")


def create_default_fallback_configuration() -> Dict[str, List[str]]:
    """Create a default fallback configuration for common models"""
    return {
        # OpenAI models
        "openai/gpt-4o": ["openai/gpt-4o-mini", "deepseek-r1"],
        "openai/gpt-4o-mini": ["deepseek-r1", "openai/gpt-4o"],
        
        # Anthropic models (if available)
        "anthropic/claude-3-sonnet": ["anthropic/claude-3-haiku", "deepseek-r1"],
        "anthropic/claude-3-haiku": ["deepseek-r1", "anthropic/claude-3-sonnet"],
        
        # DeepSeek models
        "deepseek-r1": ["openai/gpt-4o-mini", "openai/gpt-4o"],
        
        # Generic fallbacks for unknown models
        "default": ["deepseek-r1", "openai/gpt-4o-mini"]
    }


if __name__ == "__main__":
    # Example usage and testing
    from llm_client import LLMClient
    
    print("Testing Error Handling and Recovery System")
    print("=" * 50)
    
    # Initialize components
    llm_client = LLMClient()
    failure_handler = ModelFailureHandler(llm_client)
    degradation_manager = GracefulDegradationManager()
    
    # Set up fallback configuration
    fallback_config = create_default_fallback_configuration()
    failure_handler.set_fallback_models(fallback_config)
    
    # Test model validation with error handling
    test_models = ["deepseek-r1", "invalid-model-name", "openai/gpt-4o-mini"]
    
    for model in test_models:
        print(f"\nTesting model: {model}")
        try:
            messages = [{"role": "user", "content": "Hello, this is a test."}]
            content, reasoning = failure_handler.call_with_retry(
                model_name=model,
                messages=messages,
                player_name="TestPlayer"
            )
            print(f"✓ Success: {content[:50]}...")
        except ModelFailureException as e:
            print(f"✗ Failed: {e}")
            
            # Test graceful degradation
            degradation_result = degradation_manager.handle_player_model_failure(
                "TestPlayer", model, e
            )
            print(f"  Degradation applied: {degradation_result['degraded']}")
    
    # Display statistics
    print(f"\nFailure Statistics:")
    stats = failure_handler.get_failure_statistics()
    for key, value in stats.items():
        if value:  # Only show non-empty stats
            print(f"  {key}: {value}")
    
    print(f"\nDegradation Status:")
    degradation_status = degradation_manager.get_degradation_status()
    for key, value in degradation_status.items():
        if value:  # Only show non-empty status
            print(f"  {key}: {value}")