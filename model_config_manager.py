"""
Model Configuration Management System

This module provides centralized management of LLM model configurations,
including validation, preset management, and integration with the existing
LLMClient system.
"""

import json
import os
from typing import Dict, List, Optional, Any
from pathlib import Path
from llm_client import LLMClient
from error_handling import ModelFailureHandler, GracefulDegradationManager, create_default_fallback_configuration


class ModelConfigManager:
    """
    Manages LLM model configurations, validation, and presets for multi-model games.
    
    This class provides:
    - Model availability validation through LLMClient integration
    - Configuration preset management (load/save/validate)
    - Player and judge configuration generation
    - Model discovery and validation
    """
    
    def __init__(self, llm_client: LLMClient, presets_dir: str = "model_presets"):
        """
        Initialize the ModelConfigManager.
        
        Args:
            llm_client: LLMClient instance for model validation
            presets_dir: Directory to store configuration presets
        """
        self.llm_client = llm_client
        self.presets_dir = Path(presets_dir)
        self.presets_dir.mkdir(exist_ok=True)
        
        # Cache for validated models to avoid repeated API calls
        self._validated_models: Dict[str, bool] = {}
        
        # Initialize error handling components
        self.failure_handler = ModelFailureHandler(llm_client)
        self.degradation_manager = GracefulDegradationManager()
        
        # Set up default fallback configuration
        fallback_config = create_default_fallback_configuration()
        self.failure_handler.set_fallback_models(fallback_config)
    
    def validate_model(self, model_name: str, use_error_handling: bool = True) -> bool:
        """
        Validate that a model is available through the LLM client.
        
        Args:
            model_name: Name of the model to validate
            use_error_handling: Whether to use the error handling system for validation
            
        Returns:
            bool: True if model is available, False otherwise
        """
        # Check cache first
        if model_name in self._validated_models:
            return self._validated_models[model_name]
        
        try:
            # Test the model with a simple message
            test_messages = [{"role": "user", "content": "Hello"}]
            
            if use_error_handling:
                # Use error handling system for validation
                try:
                    content, _ = self.failure_handler.call_with_retry(
                        model_name=model_name,
                        messages=test_messages,
                        player_name="ModelValidator"
                    )
                    is_valid = content.strip() != ""
                    
                    if is_valid:
                        print(f"✓ Model '{model_name}' validation successful")
                    else:
                        print(f"✗ Model '{model_name}' validation failed: empty response")
                        
                except Exception as e:
                    is_valid = False
                    print(f"✗ Model '{model_name}' validation failed: {str(e)}")
            else:
                # Legacy validation method
                is_valid = self._legacy_validate_model(model_name)
            
        except Exception as e:
            is_valid = False
            print(f"✗ Model '{model_name}' validation failed: {str(e)}")
        
        # Cache the result
        self._validated_models[model_name] = is_valid
        return is_valid
    
    def _legacy_validate_model(self, model_name: str) -> bool:
        """Legacy model validation method for backward compatibility"""
        import io
        from contextlib import redirect_stdout, redirect_stderr
        
        captured_output = io.StringIO()
        
        try:
            test_messages = [{"role": "user", "content": "Hello"}]
            
            # Capture both stdout and stderr to detect error messages
            with redirect_stdout(captured_output), redirect_stderr(captured_output):
                content, _ = self.llm_client.chat(test_messages, model=model_name)
            
            output_text = captured_output.getvalue()
            
            # Check for error indicators in the output
            error_indicators = [
                "is not a valid model ID",
                "LLM calling error",
                "Error code:",
                "Invalid model"
            ]
            
            has_error = any(indicator in output_text for indicator in error_indicators)
            
            # Model is valid if we got content and no error indicators
            is_valid = content.strip() != "" and not has_error
            
            if is_valid:
                print(f"Model '{model_name}' validation successful")
            else:
                print(f"Model '{model_name}' validation failed: {output_text.strip() if has_error else 'empty response'}")
            
            return is_valid
            
        except Exception as e:
            print(f"Model '{model_name}' validation failed: {str(e)}")
            return False
    
    def get_available_models(self) -> List[str]:
        """
        Get list of available models from validation cache.
        
        Returns:
            List[str]: List of validated model names
        """
        return [model for model, is_valid in self._validated_models.items() if is_valid]
    
    def load_preset(self, preset_name: str) -> Dict[str, Any]:
        """
        Load a configuration preset from file.
        
        Args:
            preset_name: Name of the preset to load
            
        Returns:
            Dict: Preset configuration
            
        Raises:
            FileNotFoundError: If preset file doesn't exist
            ValueError: If preset file is invalid JSON or missing required fields
        """
        preset_file = self.presets_dir / f"{preset_name}.json"
        
        if not preset_file.exists():
            raise FileNotFoundError(f"Preset '{preset_name}' not found at {preset_file}")
        
        try:
            with open(preset_file, 'r', encoding='utf-8') as f:
                preset_data = json.load(f)
            
            # Validate preset structure
            self._validate_preset_structure(preset_data)
            
            print(f"Loaded preset '{preset_name}' successfully")
            return preset_data
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in preset '{preset_name}': {str(e)}")
        except Exception as e:
            raise ValueError(f"Error loading preset '{preset_name}': {str(e)}")
    
    def save_preset(self, preset_name: str, config: Dict[str, Any]) -> None:
        """
        Save a configuration preset to file.
        
        Args:
            preset_name: Name for the preset
            config: Configuration data to save
            
        Raises:
            ValueError: If config structure is invalid
        """
        # Validate preset structure before saving
        self._validate_preset_structure(config)
        
        preset_file = self.presets_dir / f"{preset_name}.json"
        
        try:
            with open(preset_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            print(f"Saved preset '{preset_name}' to {preset_file}")
            
        except Exception as e:
            raise ValueError(f"Error saving preset '{preset_name}': {str(e)}")
    
    def create_player_configs(self, models: List[str], names: List[str]) -> List[Dict[str, str]]:
        """
        Create player configurations from model and name lists.
        
        Args:
            models: List of model names for players
            names: List of player names
            
        Returns:
            List[Dict]: List of player configurations
            
        Raises:
            ValueError: If lists have different lengths or contain invalid models
        """
        if len(models) != len(names):
            raise ValueError(f"Models list length ({len(models)}) must match names list length ({len(names)})")
        
        if len(models) > 4:
            raise ValueError("Maximum 4 players supported")
        
        # Validate all models
        invalid_models = []
        for model in models:
            if not self.validate_model(model):
                invalid_models.append(model)
        
        if invalid_models:
            raise ValueError(f"Invalid models: {', '.join(invalid_models)}")
        
        # Create configurations
        configs = []
        for name, model in zip(names, models):
            configs.append({
                "name": name,
                "model": model
            })
        
        return configs
    
    def create_judge_configs(self, models: List[str], names: List[str]) -> List[Dict[str, str]]:
        """
        Create judge configurations from model and name lists.
        
        Args:
            models: List of model names for judges
            names: List of judge names
            
        Returns:
            List[Dict]: List of judge configurations
            
        Raises:
            ValueError: If lists have different lengths or contain invalid models
        """
        if len(models) != len(names):
            raise ValueError(f"Models list length ({len(models)}) must match names list length ({len(names)})")
        
        if len(models) > 4:
            raise ValueError("Maximum 4 judges supported")
        
        # Validate all models (allow duplicate models for judges)
        invalid_models = []
        for model in set(models):  # Only validate unique models
            if not self.validate_model(model):
                invalid_models.append(model)
        
        if invalid_models:
            raise ValueError(f"Invalid models: {', '.join(invalid_models)}")
        
        # Create configurations
        configs = []
        for name, model in zip(names, models):
            configs.append({
                "name": name,
                "model": model
            })
        
        return configs
    
    def list_presets(self) -> List[str]:
        """
        List all available preset names.
        
        Returns:
            List[str]: List of preset names (without .json extension)
        """
        preset_files = self.presets_dir.glob("*.json")
        return [f.stem for f in preset_files]
    
    def validate_preset_models(self, preset_name: str) -> Dict[str, bool]:
        """
        Validate all models in a preset configuration.
        
        Args:
            preset_name: Name of the preset to validate
            
        Returns:
            Dict[str, bool]: Mapping of model names to validation results
            
        Raises:
            FileNotFoundError: If preset doesn't exist
        """
        preset_data = self.load_preset(preset_name)
        
        # Collect all unique models from the preset
        models_to_validate = set()
        
        for player_config in preset_data.get("player_configs", []):
            models_to_validate.add(player_config["model"])
        
        for judge_config in preset_data.get("judge_configs", []):
            models_to_validate.add(judge_config["model"])
        
        # Validate each unique model
        validation_results = {}
        for model in models_to_validate:
            validation_results[model] = self.validate_model(model)
        
        return validation_results
    
    def get_failure_handler(self) -> ModelFailureHandler:
        """Get the failure handler instance"""
        return self.failure_handler
    
    def get_degradation_manager(self) -> GracefulDegradationManager:
        """Get the degradation manager instance"""
        return self.degradation_manager
    
    def configure_fallback_models(self, fallback_config: Dict[str, List[str]]) -> None:
        """
        Configure fallback models for error handling.
        
        Args:
            fallback_config: Dictionary mapping primary models to fallback lists
        """
        self.failure_handler.set_fallback_models(fallback_config)
        print(f"Configured fallback models for {len(fallback_config)} primary models")
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get comprehensive error handling statistics"""
        return {
            "failure_statistics": self.failure_handler.get_failure_statistics(),
            "degradation_status": self.degradation_manager.get_degradation_status()
        }
    
    def validate_all_presets(self) -> Dict[str, Dict[str, Any]]:
        """
        Validate all available presets and their models.
        
        Returns:
            Dict: Validation results for all presets
        """
        preset_names = self.list_presets()
        validation_results = {}
        
        for preset_name in preset_names:
            try:
                # Load and validate preset structure
                preset_data = self.load_preset(preset_name)
                
                # Validate all models in the preset
                model_validation = self.validate_preset_models(preset_name)
                
                # Count valid/invalid models
                valid_models = sum(1 for is_valid in model_validation.values() if is_valid)
                total_models = len(model_validation)
                
                validation_results[preset_name] = {
                    "structure_valid": True,
                    "model_validation": model_validation,
                    "valid_models": valid_models,
                    "total_models": total_models,
                    "all_models_valid": valid_models == total_models,
                    "description": preset_data.get("description", "No description"),
                    "error": None
                }
                
            except Exception as e:
                validation_results[preset_name] = {
                    "structure_valid": False,
                    "model_validation": {},
                    "valid_models": 0,
                    "total_models": 0,
                    "all_models_valid": False,
                    "description": "Error loading preset",
                    "error": str(e)
                }
        
        return validation_results
    
    def get_preset_recommendations(self) -> Dict[str, str]:
        """
        Get recommendations for which presets to use for different scenarios.
        
        Returns:
            Dict: Mapping of scenario types to recommended preset names
        """
        return {
            "single_model_testing": "single_gpt4o",
            "provider_comparison": "gpt_vs_claude", 
            "size_comparison": "size_comparison",
            "mixed_provider_research": "mixed_providers",
            "diverse_research": "research_diverse",
            "extended_research": "research_extended",
            "baseline_testing": "single_model_test"
        }
    
    def create_custom_preset_from_template(self, preset_name: str, template_type: str, 
                                         player_models: List[str], judge_models: List[str],
                                         player_names: Optional[List[str]] = None,
                                         judge_names: Optional[List[str]] = None,
                                         description: Optional[str] = None) -> None:
        """
        Create a custom preset from a template.
        
        Args:
            preset_name: Name for the new preset
            template_type: Type of template (single, mixed, research)
            player_models: List of models for players
            judge_models: List of models for judges
            player_names: Optional custom player names
            judge_names: Optional custom judge names
            description: Optional description for the preset
        """
        # Generate default names if not provided
        if player_names is None:
            player_names = [f"Player-{i+1}" for i in range(len(player_models))]
        
        if judge_names is None:
            judge_names = [f"Judge-{i+1}" for i in range(len(judge_models))]
        
        # Create player and judge configs
        player_configs = self.create_player_configs(player_models, player_names)
        judge_configs = self.create_judge_configs(judge_models, judge_names)
        
        # Generate description if not provided
        if description is None:
            unique_models = set(player_models + judge_models)
            description = f"Custom {template_type} preset with {len(unique_models)} unique models"
        
        # Create preset configuration
        preset_config = {
            "preset_name": preset_name,
            "description": description,
            "template_type": template_type,
            "player_configs": player_configs,
            "judge_configs": judge_configs
        }
        
        # Save the preset
        self.save_preset(preset_name, preset_config)
    
    def _validate_preset_structure(self, preset_data: Dict[str, Any]) -> None:
        """
        Validate the structure of a preset configuration.
        
        Args:
            preset_data: Preset configuration to validate
            
        Raises:
            ValueError: If preset structure is invalid
        """
        required_fields = ["preset_name", "player_configs", "judge_configs"]
        
        for field in required_fields:
            if field not in preset_data:
                raise ValueError(f"Missing required field '{field}' in preset")
        
        # Validate player configs
        player_configs = preset_data["player_configs"]
        if not isinstance(player_configs, list):
            raise ValueError("player_configs must be a list")
        
        if len(player_configs) > 4:
            raise ValueError("Maximum 4 players supported")
        
        for i, config in enumerate(player_configs):
            if not isinstance(config, dict):
                raise ValueError(f"Player config {i} must be a dictionary")
            
            if "name" not in config or "model" not in config:
                raise ValueError(f"Player config {i} must have 'name' and 'model' fields")
        
        # Validate judge configs
        judge_configs = preset_data["judge_configs"]
        if not isinstance(judge_configs, list):
            raise ValueError("judge_configs must be a list")
        
        if len(judge_configs) > 4:
            raise ValueError("Maximum 4 judges supported")
        
        for i, config in enumerate(judge_configs):
            if not isinstance(config, dict):
                raise ValueError(f"Judge config {i} must be a dictionary")
            
            if "name" not in config or "model" not in config:
                raise ValueError(f"Judge config {i} must have 'name' and 'model' fields")


def create_default_presets(manager: ModelConfigManager) -> None:
    """
    Create comprehensive default preset configurations for common research scenarios.
    
    Args:
        manager: ModelConfigManager instance to save presets to
    """
    presets_to_create = []
    
    # Only create presets that don't already exist
    existing_presets = set(manager.list_presets())
    
    # Single model preset (all players use same model)
    if "single_model_test" not in existing_presets:
        single_model_preset = {
            "preset_name": "single_model_test",
            "description": "All players and judges use the same model for testing",
            "player_configs": [
                {"name": "Player-1", "model": "gpt-4o"},
                {"name": "Player-2", "model": "gpt-4o"},
                {"name": "Player-3", "model": "gpt-4o"},
                {"name": "Player-4", "model": "gpt-4o"}
            ],
            "judge_configs": [
                {"name": "Justice", "model": "gpt-4o"},
                {"name": "Wisdom", "model": "gpt-4o"},
                {"name": "Truth", "model": "gpt-4o"},
                {"name": "Honor", "model": "gpt-4o"}
            ]
        }
        presets_to_create.append(("single_model_test", single_model_preset))
    
    # Mixed model preset (example with different models)
    if "mixed_models_example" not in existing_presets:
        mixed_model_preset = {
            "preset_name": "mixed_models_example",
            "description": "Example configuration with different models (update models as needed)",
            "player_configs": [
                {"name": "GPT-Alpha", "model": "gpt-4o"},
                {"name": "GPT-Beta", "model": "gpt-4o-mini"},
                {"name": "Claude-Alpha", "model": "claude-3-sonnet"},
                {"name": "Claude-Beta", "model": "claude-3-haiku"}
            ],
            "judge_configs": [
                {"name": "Justice", "model": "gpt-4o"},
                {"name": "Wisdom", "model": "gpt-4o-mini"},
                {"name": "Truth", "model": "claude-3-sonnet"},
                {"name": "Honor", "model": "claude-3-haiku"}
            ]
        }
        presets_to_create.append(("mixed_models_example", mixed_model_preset))
    
    # Create any missing presets
    created_presets = []
    for preset_name, preset_config in presets_to_create:
        try:
            manager.save_preset(preset_name, preset_config)
            created_presets.append(preset_name)
        except Exception as e:
            print(f"Error creating preset '{preset_name}': {str(e)}")
    
    if created_presets:
        print(f"Created default presets: {', '.join(created_presets)}")
    else:
        print("All default presets already exist")
    
    # Display all available presets
    all_presets = manager.list_presets()
    print(f"Available presets ({len(all_presets)}): {', '.join(sorted(all_presets))}")
    
    # Show preset recommendations
    recommendations = manager.get_preset_recommendations()
    print("\nPreset recommendations:")
    for scenario, preset_name in recommendations.items():
        if preset_name in all_presets:
            print(f"  {scenario}: {preset_name}")
        else:
            print(f"  {scenario}: {preset_name} (not available)")


if __name__ == "__main__":
    # Example usage and testing
    llm_client = LLMClient()
    manager = ModelConfigManager(llm_client)
    
    # Create default presets
    create_default_presets(manager)
    
    # Test model validation
    print("\nTesting model validation:")
    test_models = ["deepseek-r1", "invalid-model", "gpt-4o"]
    for model in test_models:
        is_valid = manager.validate_model(model)
        print(f"Model '{model}': {'Valid' if is_valid else 'Invalid'}")
    
    # List available presets
    print(f"\nAvailable presets: {manager.list_presets()}")
    
    # Test loading a preset
    try:
        preset = manager.load_preset("single_model_test")
        print(f"\nLoaded preset: {preset['preset_name']}")
        print(f"Description: {preset['description']}")
    except Exception as e:
        print(f"Error loading preset: {str(e)}")