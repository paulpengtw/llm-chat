import random
import json
import re
from typing import List, Dict
from llm_client import LLMClient

RULE_BASE_PATH = "prompt/rule_base.txt"
PLAY_CARD_PROMPT_TEMPLATE_PATH = "prompt/play_card_prompt_template.txt"
CHALLENGE_PROMPT_TEMPLATE_PATH = "prompt/challenge_prompt_template.txt"
REFLECT_PROMPT_TEMPLATE_PATH = "prompt/reflect_prompt_template.txt"

class Player:
    def __init__(self, name: str, model_name: str):
        """Initialize player
        
        Args:
            name: Player name
            model_name: Name of LLM model to use
        """
        self.name = name
        self.hand = []  # Holds stance cards
        self.opinions = {}  # Tracks opinions about other players
        
        # LLM initialization
        self.llm_client = LLMClient()
        self.model_name = model_name

    def _read_file(self, filepath: str) -> str:
        """Read file content"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except Exception as e:
            print(f"Error reading file {filepath}: {str(e)}")
            return ""

    def print_status(self) -> None:
        """Print player status"""
        print(f"{self.name} - Current stances: {', '.join(self.hand)}")
        
    def init_opinions(self, other_players: List["Player"]) -> None:
        """Initialize opinions about other players
        
        Args:
            other_players: List of other players
        """
        self.opinions = {
            player.name: "No impression yet of this debater"
            for player in other_players
            if player.name != self.name
        }

    def choose_cards_to_play(self,
                        round_base_info: str,
                        round_action_info: str,
                        play_decision_info: str) -> Dict:
        """Choose stance cards to play
        
        Args:
            round_base_info: Round base information
            round_action_info: Round action information
            play_decision_info: Play decision information
            
        Returns:
            tuple: (Result dict, Reasoning content)
            - Result dict includes played_cards, behavior and play_reason
            - Reasoning content is LLM's original reasoning
        """
        # Read rules and template
        rules = self._read_file(RULE_BASE_PATH)
        template = self._read_file(PLAY_CARD_PROMPT_TEMPLATE_PATH)
        
        # Prepare current hand info
        current_cards = ", ".join(self.hand)
        
        # Fill template
        prompt = template.format(
            rules=rules,
            self_name=self.name,
            round_base_info=round_base_info,
            round_action_info=round_action_info,
            play_decision_info=play_decision_info,
            current_cards=current_cards
        )
        
        # Try to get valid JSON response, max 5 attempts
        for attempt in range(5):
            messages = [
                {"role": "user", "content": prompt}
            ]
            
            try:
                content, reasoning_content = self.llm_client.chat(messages, model=self.model_name)
                
                # Try to extract JSON
                json_match = re.search(r'({[\s\S]*})', content)
                if json_match:
                    json_str = json_match.group(1)
                    result = json.loads(json_str)
                    
                    # Validate JSON format
                    if all(key in result for key in ["played_cards", "behavior", "play_reason"]):
                        # Ensure played_cards is a list
                        if not isinstance(result["played_cards"], list):
                            result["played_cards"] = [result["played_cards"]]
                        
                        # Validate cards are valid
                        valid_cards = all(card in self.hand for card in result["played_cards"])
                        valid_count = 1 <= len(result["played_cards"]) <= 3
                        
                        if valid_cards and valid_count:
                            # Remove played cards from hand
                            for card in result["played_cards"]:
                                self.hand.remove(card)
                            return result, reasoning_content
                                
            except Exception as e:
                print(f"Attempt {attempt+1} failed: {str(e)}")
        raise RuntimeError(f"Player {self.name}'s choose_cards_to_play failed after multiple attempts")

    def decide_challenge(self,
                        round_base_info: str,
                        round_action_info: str,
                        challenge_decision_info: str,
                        challenging_player_performance: str,
                        extra_hint: str) -> bool:
        """Decide whether to challenge previous player's argument
        
        Args:
            round_base_info: Round base information
            round_action_info: Round action information
            challenge_decision_info: Challenge decision information
            challenging_player_performance: Challenged player's performance
            extra_hint: Additional hint
            
        Returns:
            tuple: (Result dict, Reasoning content)
            - Result dict includes was_challenged and challenge_reason
            - Reasoning content is LLM's original reasoning
        """
        # Read rules and template
        rules = self._read_file(RULE_BASE_PATH)
        template = self._read_file(CHALLENGE_PROMPT_TEMPLATE_PATH)
        self_hand = f"Your current stances: {', '.join(self.hand)}"
        
        # Fill template
        prompt = template.format(
            rules=rules,
            self_name=self.name,
            round_base_info=round_base_info,
            round_action_info=round_action_info,
            self_hand=self_hand,
            challenge_decision_info=challenge_decision_info,
            challenging_player_performance=challenging_player_performance,
            extra_hint=extra_hint
        )
        
        # Try to get valid JSON response, max 5 attempts
        for attempt in range(5):
            messages = [
                {"role": "user", "content": prompt}
            ]
            
            try:
                content, reasoning_content = self.llm_client.chat(messages, model=self.model_name)
                
                # Parse JSON response
                json_match = re.search(r'({[\s\S]*})', content)
                if json_match:
                    json_str = json_match.group(1)
                    result = json.loads(json_str)
                    
                    # Validate JSON format
                    if all(key in result for key in ["was_challenged", "challenge_reason"]):
                        if isinstance(result["was_challenged"], bool):
                            return result, reasoning_content
                
            except Exception as e:
                print(f"Attempt {attempt+1} failed: {str(e)}")
        raise RuntimeError(f"Player {self.name}'s decide_challenge failed after multiple attempts")

    def reflect(self, alive_players: List[str], round_base_info: str, round_action_info: str, round_result: str) -> None:
        """Reflect on the debate round and update impressions
        
        Args:
            alive_players: List of player names
            round_base_info: Round base information
            round_action_info: Round action information
            round_result: Round result
        """
        # Read reflection template
        template = self._read_file(REFLECT_PROMPT_TEMPLATE_PATH)
        
        # Read rules
        rules = self._read_file(RULE_BASE_PATH)
        
        # Reflect on each player (except self)
        for player_name in alive_players:
            if player_name == self.name:
                continue
            
            # Get previous opinion
            previous_opinion = self.opinions.get(player_name, "No impression yet of this debater")
            
            # Fill template
            prompt = template.format(
                rules=rules,
                self_name=self.name,
                round_base_info=round_base_info,
                round_action_info=round_action_info,
                round_result=round_result,
                player=player_name,
                previous_opinion=previous_opinion
            )
            
            # Request LLM analysis
            messages = [
                {"role": "user", "content": prompt}
            ]
            
            try:
                content, _ = self.llm_client.chat(messages, model=self.model_name)
                
                # Update opinion
                self.opinions[player_name] = content.strip()
                print(f"{self.name} updated opinion of {player_name}")
                
            except Exception as e:
                print(f"Error reflecting on {player_name}: {str(e)}")
