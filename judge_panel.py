import json
import os
from typing import Dict, List, Optional
from player import Player
from llm_client import LLMClient

class JudgePanel:
    def __init__(self, judge_configs: List[Dict[str, str]], enable_human_scoring: bool = False):
        """Initialize the judge panel
        
        Args:
            judge_configs: List of judge configurations, each containing name and model
            enable_human_scoring: Whether to enable human scoring integration
        """
        self.judges = []
        for config in judge_configs:
            llm = LLMClient()
            self.judges.append({"name": config["name"], "model": config["model"], "client": llm})
        self.current_votes = {}
        self.judge_prompt = self._load_judge_prompt()
        self.player_scores = {}  # Track scores for each player
        
        # Human scoring integration
        self.enable_human_scoring = enable_human_scoring
        self.human_scoring_interface = None
        self.current_human_scores = {}
        
        # Display judge model assignments
        print("Judge Panel Initialized:")
        for judge in self.judges:
            print(f"  {judge['name']} -> {judge['model']}")
        print()

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
        # Since we removed penalty functionality, result is always None
        prompt = prompt.replace("%round_result%", "null")

        # Collect votes from each judge
        for judge in self.judges:
            print(f"Collecting evaluation from {judge['name']} ({judge['model']})...")
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
                    "metrics": vote_data.get("performance_metrics", {}),
                    "judge_model": judge["model"]
                }
                print(f"  {judge['name']} ({judge['model']}) completed evaluation")
            except (ValueError, json.JSONDecodeError, KeyError) as e:
                print(f"Error parsing judge {judge['name']} ({judge['model']})'s response: {e}")
                print(f"Raw response: {response}")
                # If parsing fails, record a null vote
                self.current_votes[judge["name"]] = {
                    "voted_player": None,
                    "reasoning": "Error in vote parsing",
                    "metrics": {},
                    "judge_model": judge["model"]
                }

    def reveal_votes(self) -> Dict:
        """Reveal all collected votes and update player scores
        
        Returns:
            Dict containing vote summary and updated scores
        """
        vote_counts = {}
        for judge_name, vote in self.current_votes.items():
            player = vote["voted_player"]
            if player:
                vote_counts[player] = vote_counts.get(player, 0) + 1
                self.player_scores[player] = self.player_scores.get(player, 0) + 1

        # Add model information to votes for better display
        enhanced_votes = {}
        for judge_name, vote_info in self.current_votes.items():
            model = next((j['model'] for j in self.judges if j['name'] == judge_name), 'Unknown')
            enhanced_votes[judge_name] = {
                **vote_info,
                'judge_model': model
            }

        return {
            "votes": enhanced_votes,
            "vote_counts": vote_counts,
            "current_scores": self.player_scores
        }

    def set_human_scoring_interface(self, interface) -> None:
        """Set the human scoring interface for collecting human judge scores
        
        Args:
            interface: HumanScoringInterface instance
        """
        self.human_scoring_interface = interface
        self.enable_human_scoring = True

    def evaluate_round_with_human_input(self, round_info: Dict) -> Dict:
        """Evaluate a round with both AI judges and human scoring
        
        Args:
            round_info: Information about the current round for evaluation
            
        Returns:
            Dict containing both AI votes and human scores
        """
        # First collect AI judge votes
        self.evaluate_round(round_info)
        ai_results = self.reveal_votes()
        
        # Collect human scores if enabled
        human_scores = {}
        if self.enable_human_scoring and self.human_scoring_interface:
            try:
                print("\n" + "="*50)
                print("HUMAN SCORING SESSION STARTING")
                print("="*50)
                print(f"Please score the performance of each player in Round {round_info.get('round_id', 'N/A')}")
                print(f"Scoring interface: http://127.0.0.1:{self.human_scoring_interface.web_port}")
                print("="*50)
                
                # Extract player names from round info
                players = round_info.get('round_players', [])
                if not players:
                    # Fallback to extracting from action_info if available
                    action_info = round_info.get('action_info', {})
                    players = list(action_info.keys()) if action_info else []
                
                if players:
                    # Start scoring session
                    self.human_scoring_interface.start_scoring_session(
                        round_info=round_info,
                        players=players,
                        timeout=300  # 5 minutes timeout
                    )
                    
                    # Collect scores
                    human_scores = self.human_scoring_interface.collect_scores(timeout=300)
                    self.current_human_scores = human_scores
                    
                    if human_scores:
                        print("\n✅ Human scores collected successfully!")
                    else:
                        print("\n⚠️  No human scores collected (timeout or no input)")
                else:
                    print("\n⚠️  No players found for human scoring")
                    
            except Exception as e:
                print(f"\n❌ Error during human scoring: {e}")
                human_scores = {}
        
        # Combine results
        combined_results = {
            'ai_evaluation': ai_results,
            'human_scores': human_scores,
            'round_info': round_info
        }
        
        return combined_results

    def display_combined_round_summary(self, round_info: Dict) -> None:
        """Display a comprehensive summary using both AI votes and human scores
        
        Args:
            round_info: Information about the round being summarized
        """
        if self.human_scoring_interface and self.current_human_scores:
            # Use the human scoring interface's display method for consistency
            ai_results = self.reveal_votes()
            self.human_scoring_interface.display_round_summary(
                round_info=round_info,
                ai_votes=ai_results,
                human_scores=self.current_human_scores
            )
        else:
            # Fallback to our own display method
            print(self.get_combined_evaluation_summary())

    def get_combined_evaluation_summary(self) -> str:
        """Get a formatted summary of both AI and human evaluations
        
        Returns:
            Formatted string showing combined evaluation results
        """
        summary = "\n" + "="*60 + "\n"
        summary += "COMBINED EVALUATION SUMMARY\n"
        summary += "="*60 + "\n"
        
        # AI Judge Results
        summary += "\nAI JUDGE VOTES:\n"
        summary += "-" * 30 + "\n"
        
        if self.current_votes:
            vote_counts = {}
            for judge_name, vote_info in self.current_votes.items():
                voted_player = vote_info.get('voted_player', 'None')
                reasoning = vote_info.get('reasoning', 'No reasoning provided')
                model = next((j['model'] for j in self.judges if j['name'] == judge_name), 'Unknown')
                
                summary += f"{judge_name} ({model}): {voted_player}\n"
                summary += f"  Reasoning: {reasoning[:80]}{'...' if len(reasoning) > 80 else ''}\n"
                
                # Count votes
                if voted_player and voted_player != 'None':
                    vote_counts[voted_player] = vote_counts.get(voted_player, 0) + 1
            
            summary += f"\nAI Vote Counts: {vote_counts}\n"
        else:
            summary += "No AI votes recorded\n"
        
        # Human Scoring Results
        summary += "\nHUMAN JUDGE SCORES:\n"
        summary += "-" * 30 + "\n"
        
        if self.current_human_scores:
            for player_name, scores in self.current_human_scores.items():
                summary += f"{player_name}:\n"
                for criterion, score in scores.items():
                    criterion_display = criterion.replace('_', ' ').title()
                    summary += f"  {criterion_display}: {score}/5\n"
                
                # Calculate average score
                if scores:
                    avg_score = sum(scores.values()) / len(scores)
                    summary += f"  Average: {avg_score:.1f}/5\n"
                summary += "\n"
            
            # Overall human scoring summary
            summary += "Human Scoring Summary:\n"
            player_averages = {}
            for player_name, scores in self.current_human_scores.items():
                if scores:
                    avg = sum(scores.values()) / len(scores)
                    player_averages[player_name] = avg
            
            if player_averages:
                sorted_players = sorted(player_averages.items(), key=lambda x: x[1], reverse=True)
                summary += f"Top Human-Rated Player: {sorted_players[0][0]} ({sorted_players[0][1]:.1f}/5)\n"
        else:
            summary += "No human scores collected\n"
        
        # Combined Analysis
        summary += "\nCOMBINED ANALYSIS:\n"
        summary += "-" * 30 + "\n"
        
        if self.current_votes and self.current_human_scores:
            # Find AI vote winner
            ai_vote_counts = {}
            for vote_info in self.current_votes.values():
                voted_player = vote_info.get('voted_player')
                if voted_player and voted_player != 'None':
                    ai_vote_counts[voted_player] = ai_vote_counts.get(voted_player, 0) + 1
            
            ai_winner = max(ai_vote_counts.items(), key=lambda x: x[1])[0] if ai_vote_counts else None
            
            # Find human score winner
            human_averages = {}
            for player_name, scores in self.current_human_scores.items():
                if scores:
                    human_averages[player_name] = sum(scores.values()) / len(scores)
            
            human_winner = max(human_averages.items(), key=lambda x: x[1])[0] if human_averages else None
            
            if ai_winner and human_winner:
                if ai_winner == human_winner:
                    summary += f"✅ CONSENSUS: Both AI judges and human scorer agree on {ai_winner}\n"
                else:
                    summary += f"🤔 DISAGREEMENT: AI judges favor {ai_winner}, human scorer favors {human_winner}\n"
            elif ai_winner:
                summary += f"AI judges favor: {ai_winner} (no human scores for comparison)\n"
            elif human_winner:
                summary += f"Human scorer favors: {human_winner} (no clear AI consensus)\n"
        elif self.current_votes:
            summary += "Only AI evaluation available\n"
        elif self.current_human_scores:
            summary += "Only human evaluation available\n"
        else:
            summary += "No evaluation data available\n"
        
        summary += "="*60 + "\n"
        return summary

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
