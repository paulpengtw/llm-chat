#!/usr/bin/env python3
"""
Test script for validating model configuration presets.

This script tests the preset management functionality and validates
all available presets without requiring actual model API calls.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any


def validate_preset_structure(preset_data: Dict[str, Any], preset_name: str) -> Dict[str, Any]:
    """
    Validate the structure of a preset configuration.
    
    Args:
        preset_data: Preset configuration to validate
        preset_name: Name of the preset for error reporting
        
    Returns:
        Dict: Validation results
    """
    errors = []
    warnings = []
    
    # Check required fields
    required_fields = ["preset_name", "player_configs", "judge_configs"]
    for field in required_fields:
        if field not in preset_data:
            errors.append(f"Missing required field '{field}'")
    
    # Check optional fields
    if "description" not in preset_data:
        warnings.append("Missing description field")
    
    # Validate player configs
    if "player_configs" in preset_data:
        player_configs = preset_data["player_configs"]
        if not isinstance(player_configs, list):
            errors.append("player_configs must be a list")
        elif len(player_configs) > 4:
            errors.append("Maximum 4 players supported")
        elif len(player_configs) == 0:
            errors.append("At least 1 player required")
        else:
            for i, config in enumerate(player_configs):
                if not isinstance(config, dict):
                    errors.append(f"Player config {i} must be a dictionary")
                elif "name" not in config or "model" not in config:
                    errors.append(f"Player config {i} must have 'name' and 'model' fields")
    
    # Validate judge configs
    if "judge_configs" in preset_data:
        judge_configs = preset_data["judge_configs"]
        if not isinstance(judge_configs, list):
            errors.append("judge_configs must be a list")
        elif len(judge_configs) > 4:
            errors.append("Maximum 4 judges supported")
        elif len(judge_configs) == 0:
            errors.append("At least 1 judge required")
        else:
            for i, config in enumerate(judge_configs):
                if not isinstance(config, dict):
                    errors.append(f"Judge config {i} must be a dictionary")
                elif "name" not in config or "model" not in config:
                    errors.append(f"Judge config {i} must have 'name' and 'model' fields")
    
    # Check for duplicate player names
    if "player_configs" in preset_data:
        player_names = [config.get("name") for config in preset_data["player_configs"]]
        if len(player_names) != len(set(player_names)):
            warnings.append("Duplicate player names detected")
    
    # Check for duplicate judge names
    if "judge_configs" in preset_data:
        judge_names = [config.get("name") for config in preset_data["judge_configs"]]
        if len(judge_names) != len(set(judge_names)):
            warnings.append("Duplicate judge names detected")
    
    # Collect all models
    all_models = set()
    if "player_configs" in preset_data:
        for config in preset_data["player_configs"]:
            if "model" in config:
                all_models.add(config["model"])
    
    if "judge_configs" in preset_data:
        for config in preset_data["judge_configs"]:
            if "model" in config:
                all_models.add(config["model"])
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "unique_models": list(all_models),
        "model_count": len(all_models)
    }


def test_all_presets():
    """Test all presets in the model_presets directory."""
    presets_dir = Path("model_presets")
    
    if not presets_dir.exists():
        print(f"❌ Presets directory '{presets_dir}' not found")
        return False
    
    preset_files = list(presets_dir.glob("*.json"))
    
    if not preset_files:
        print(f"❌ No preset files found in '{presets_dir}'")
        return False
    
    print(f"🔍 Testing {len(preset_files)} preset files...")
    print()
    
    all_valid = True
    preset_summary = []
    
    for preset_file in sorted(preset_files):
        preset_name = preset_file.stem
        print(f"📋 Testing preset: {preset_name}")
        
        try:
            with open(preset_file, 'r', encoding='utf-8') as f:
                preset_data = json.load(f)
            
            # Validate structure
            validation_result = validate_preset_structure(preset_data, preset_name)
            
            if validation_result["valid"]:
                print(f"  ✅ Structure valid")
                print(f"  📊 {len(preset_data.get('player_configs', []))} players, {len(preset_data.get('judge_configs', []))} judges")
                print(f"  🤖 {validation_result['model_count']} unique models")
                
                if validation_result["warnings"]:
                    print(f"  ⚠️  Warnings: {', '.join(validation_result['warnings'])}")
                
                preset_summary.append({
                    "name": preset_name,
                    "valid": True,
                    "description": preset_data.get("description", "No description"),
                    "models": validation_result["unique_models"],
                    "player_count": len(preset_data.get('player_configs', [])),
                    "judge_count": len(preset_data.get('judge_configs', []))
                })
                
            else:
                print(f"  ❌ Structure invalid")
                print(f"  🚫 Errors: {', '.join(validation_result['errors'])}")
                all_valid = False
                
                preset_summary.append({
                    "name": preset_name,
                    "valid": False,
                    "errors": validation_result["errors"]
                })
            
        except json.JSONDecodeError as e:
            print(f"  ❌ Invalid JSON: {str(e)}")
            all_valid = False
        except Exception as e:
            print(f"  ❌ Error loading preset: {str(e)}")
            all_valid = False
        
        print()
    
    # Print summary
    print("=" * 60)
    print("📊 PRESET VALIDATION SUMMARY")
    print("=" * 60)
    
    valid_presets = [p for p in preset_summary if p.get("valid", False)]
    invalid_presets = [p for p in preset_summary if not p.get("valid", False)]
    
    print(f"✅ Valid presets: {len(valid_presets)}")
    print(f"❌ Invalid presets: {len(invalid_presets)}")
    print()
    
    if valid_presets:
        print("Valid presets:")
        for preset in valid_presets:
            print(f"  • {preset['name']}: {preset['description']}")
            print(f"    Players: {preset['player_count']}, Judges: {preset['judge_count']}, Models: {len(preset['models'])}")
        print()
    
    if invalid_presets:
        print("Invalid presets:")
        for preset in invalid_presets:
            print(f"  • {preset['name']}: {', '.join(preset.get('errors', ['Unknown error']))}")
        print()
    
    # Show model usage statistics
    all_models = set()
    for preset in valid_presets:
        all_models.update(preset['models'])
    
    print(f"🤖 Total unique models across all presets: {len(all_models)}")
    if all_models:
        print("Models used:")
        for model in sorted(all_models):
            count = sum(1 for p in valid_presets if model in p['models'])
            print(f"  • {model} (used in {count} presets)")
    
    return all_valid


if __name__ == "__main__":
    print("🧪 Model Configuration Preset Validation")
    print("=" * 60)
    
    success = test_all_presets()
    
    if success:
        print("🎉 All presets are valid!")
        exit(0)
    else:
        print("💥 Some presets have validation errors!")
        exit(1)