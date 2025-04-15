import json
import os
from typing import Dict, List, Optional
from player import Player
from llm_client import LLMClient

class JudgePanel:
    def __init__(self, judge_configs: List[Dict[str, str]]):
        """Initialize the judge panel
        
        Args:
            judge_configs: List of judge configurations, each containing name and model
        """
        self.judges = []
        for config in judge_configs:
            llm = LLMClient()
            self.judges.append({"name": config["name"], "model": config["model"], "client": llm})
        self.current_votes = {}
        self.judge_prompt = self._load_judge_prompt()
        self.player_scores = {}  # Track scores for each player

    def _load_judge_prompt(self) -> str:
        """Load the judge prompt template from file"""
        with open("prompt/judge_prompt_template.txt", "r") as f:
            return f.read()

    def initialize_scores(self, player_names: List[str]) -> None:
        """Initialize score tracking for all players
        
        Args:
            player_names: List of player names to track scores for
        """
        self.player_scores = {name: 0 for name in player_names}

    def evaluate_round(self, round_info: Dict) -> None:
        """Collect votes from all judges for the current round
        
        Args:
            round_info: Information about the current round for judges to evaluate
        """
        self.current_votes.clear()

        # Format the prompt with round information
        prompt = self.judge_prompt
        prompt = prompt.replace("%round_base_info%", json.dumps(round_info["base_info"], indent=2))
        prompt = prompt.replace("%round_action_info%", json.dumps(round_info["action_info"], indent=2))
        prompt = prompt.replace("%round_result%", json.dumps(round_info["result"], indent=2))

        # Collect votes from each judge
        for judge in self.judges:
            messages = [{"role": "user", "content": prompt}]
            response, _ = judge["client"].chat(messages, model=judge["model"])
            try:
                # Handle multi-line JSON responses
                response = response.strip()
                try:
                    # First try to parse the entire response
                    vote_data = json.loads(response)
                except json.JSONDecodeError:
                    # If that fails, try to find and parse just the JSON object
                    import re
                    json_pattern = r"\{[\s\S]*\}"  # Matches across newlines
                    match = re.search(json_pattern, response)
                    if not match:
                        raise ValueError("No JSON object found in response")
                    vote_data = json.loads(match.group(0))
                self.current_votes[judge["name"]] = {
                    "voted_player": vote_data.get("voted_player"),
                    "reasoning": vote_data.get("reasoning", "No reasoning provided"),
                    "metrics": vote_data.get("performance_metrics", {})
                }
            except (ValueError, json.JSONDecodeError, KeyError) as e:
                print(f"Error parsing judge {judge['name']}'s response: {e}")
                print(f"Raw response: {response}")
                # If parsing fails, record a null vote
                self.current_votes[judge["name"]] = {
                    "voted_player": None,
                    "reasoning": "Error in vote parsing",
                    "metrics": {}
                }

    def reveal_votes(self) -> Dict:
        """Reveal all collected votes and update player scores
        
        Returns:
            Dict containing vote summary and updated scores
        """
        vote_counts = {}
        for vote in self.current_votes.values():
            player = vote["voted_player"]
            if player:
                vote_counts[player] = vote_counts.get(player, 0) + 1
                self.player_scores[player] = self.player_scores.get(player, 0) + 1

        return {
            "votes": self.current_votes,
            "vote_counts": vote_counts,
            "current_scores": self.player_scores
        }

    def get_score_summary(self) -> str:
        """Get a formatted string of current scores
        
        Returns:
            Formatted string showing all player scores
        """
        summary = "\nCurrent Scores:\n" + "-" * 20 + "\n"
        sorted_scores = sorted(self.player_scores.items(), key=lambda x: x[1], reverse=True)
        for player, score in sorted_scores:
            summary += f"{player}: {score} points\n"
        return summary
