from dataclasses import dataclass, field
from typing import List, Dict, Optional
import datetime
import json
import os

def generate_game_id():
    """Generate game ID with timestamp"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return timestamp

@dataclass
class PlayerInitialState:
    """Record player initial state"""
    player_name: str
    bullet_position: int  # Kept for compatibility but not used
    current_gun_position: int  # Kept for compatibility but not used
    initial_hand: List[str]  # Initial stance cards
    
    def to_dict(self) -> Dict:
        return {
            "player_name": self.player_name,
            "bullet_position": self.bullet_position,
            "current_gun_position": self.current_gun_position,
            "initial_hand": self.initial_hand
        }

@dataclass
class PlayAction:
    """Record a play action"""
    player_name: str
    played_cards: List[str]  # Played stance cards
    remaining_cards: List[str]  # Remaining stance cards
    play_reason: str  # Reason for playing these cards
    behavior: str  # Player's behavior description
    next_player: str  # Next player to act
    was_challenged: bool = False  # Whether action was challenged
    challenge_reason: Optional[str] = None  # Reason for challenge
    challenge_result: Optional[bool] = None  # Challenge result
    play_thinking: Optional[str] = None  # Player's thought process
    challenge_thinking: Optional[str] = None  # Challenger's thought process
    
    def to_dict(self) -> Dict:
        return {
            "player_name": self.player_name,
            "played_cards": self.played_cards,
            "remaining_cards": self.remaining_cards,
            "play_reason": self.play_reason,
            "behavior": self.behavior,
            "next_player": self.next_player,
            "was_challenged": self.was_challenged,
            "challenge_reason": self.challenge_reason,
            "challenge_result": self.challenge_result,
            "play_thinking": self.play_thinking,
            "challenge_thinking": self.challenge_thinking
        }
    
    def update_challenge(self, was_challenged: bool, reason: str, result: bool, challenge_thinking: str = None) -> None:
        """Update challenge information"""
        self.was_challenged = was_challenged
        self.challenge_reason = reason
        self.challenge_result = result
        self.challenge_thinking = challenge_thinking

@dataclass
class RoundRecord:
    """Record a debate round"""
    round_id: int
    target_card: str  # Current debate topic
    starting_player: str
    player_initial_states: List[PlayerInitialState]
    round_players: List[str] = field(default_factory=list)
    player_opinions: Dict[str, Dict[str, str]] = field(default_factory=dict)
    play_history: List[PlayAction] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "round_id": self.round_id,
            "target_card": self.target_card,
            "round_players": self.round_players,
            "starting_player": self.starting_player,
            "player_initial_states": [ps.to_dict() for ps in self.player_initial_states],
            "player_opinions": self.player_opinions,
            "play_history": [play.to_dict() for play in self.play_history]
        }
    
    def add_play_action(self, action: PlayAction) -> None:
        """Add play action record"""
        self.play_history.append(action)
    
    def get_last_action(self) -> Optional[PlayAction]:
        """Get last play action"""
        return self.play_history[-1] if self.play_history else None

    def get_latest_round_info(self) -> str:
        """Return latest round base information"""
        return (
            f"Round {self.round_id}, Topic: {self.target_card}, "
            f"Participants: {', '.join(self.round_players)}, "
            f"Starting with {self.starting_player}"
        )

    def get_latest_round_actions(self, current_player: str, include_latest: bool = True) -> str:
        """
        Get current round action information
        
        Args:
            current_player: Current player name
            include_latest: Whether to include latest action
        
        Returns:
            str: Formatted action information
        """
        action_texts = []
        actions_to_process = self.play_history if include_latest else self.play_history[:-1]
        
        for action in actions_to_process:
            if action.player_name == current_player:
                action_texts.append(
                    f"Your turn to present arguments. You played {len(action.played_cards)} stances: "
                    f"{', '.join(action.played_cards)}, remaining stances: {', '.join(action.remaining_cards)}\n"
                    f"Your presentation: {action.behavior}"
                )
            else:
                action_texts.append(
                    f"{action.player_name}'s turn to present. They used {len(action.played_cards)} stances, "
                    f"with {len(action.remaining_cards)} remaining\n"
                    f"{action.player_name}'s presentation: {action.behavior}"
                )
            
            if action.was_challenged:
                stance_desc = f"Used stances: {', '.join(action.played_cards)}"
                challenge_result_text = (f"{stance_desc}, challenge successful" 
                                      if action.challenge_result else 
                                      f"{stance_desc}, challenge failed")
                if action.next_player == current_player:
                    challenge_text = f"You challenged {action.player_name}, {action.player_name} {challenge_result_text}"
                elif action.player_name == current_player:
                    challenge_text = f"{action.next_player} challenged you, you {challenge_result_text}"
                else:
                    challenge_text = f"{action.next_player} challenged {action.player_name}, {action.player_name} {challenge_result_text}"
            else:
                if action.next_player == current_player:
                    challenge_text = f"You accepted {action.player_name}'s argument"
                elif action.player_name == current_player:
                    challenge_text = f"{action.next_player} accepted your argument"
                else:
                    challenge_text = f"{action.next_player} accepted {action.player_name}'s argument"
            action_texts.append(challenge_text)
        
        return "\n".join(action_texts)
    
    def get_latest_play_behavior(self) -> str:
        """
        Get latest player's presentation behavior
        
        Returns:
            str: Formatted behavior description
        """
        if not self.play_history:
            return ""
            
        last_action = self.get_last_action()
        if not last_action:
            return ""
            
        return (f"{last_action.player_name} presented {len(last_action.played_cards)} stances, "
                f"with {len(last_action.remaining_cards)} remaining. "
                f"{last_action.player_name}'s presentation: {last_action.behavior}")
    
    def get_latest_round_result(self, current_player: str) -> str:
        """
        Get latest round result
        
        Args:
            current_player: Current player name
            
        Returns:
            str: Round conclusion
        """
        if not self.play_history:
            return "Round not started yet"
            
        last_action = self.get_last_action()
        if not last_action:
            return "No actions taken yet"
            
        if last_action.was_challenged:
            return f"Round concluded with challenge: {last_action.challenge_reason}"
        else:
            return "Round concluded with arguments accepted"

    def get_play_decision_info(self, self_player: str, interacting_player: str) -> str:
        """Get current round play decision information
        
        Args:
            self_player: Current player
            interacting_player: Next player
        Returns:
            str: Decision context information
        """
        opinion = self.player_opinions[self_player].get(interacting_player, "No impression yet")
        
        return (f"{interacting_player} will evaluate your argument.\n"
                f"Your analysis of {interacting_player}: {opinion}")

    def get_challenge_decision_info(self, self_player: str, interacting_player: str) -> str:
        """Get current round challenge decision information
        
        Args:
            self_player: Current player
            interacting_player: Previous player
        Returns:
            str: Challenge context information
        """
        opinion = self.player_opinions[self_player].get(interacting_player, "No impression yet")
        
        return (f"You're evaluating {interacting_player}'s argument.\n"
                f"Your analysis of {interacting_player}: {opinion}")

@dataclass
class GameRecord:
    """Complete debate game record"""
    def __init__(self):
        self.game_id: str = generate_game_id()
        self.player_names: List[str] = []
        self.rounds: List[RoundRecord] = []
        self.winner: Optional[str] = None
        self.save_directory: str = "game_records"
        
        # Ensure save directory exists
        if not os.path.exists(self.save_directory):
            os.makedirs(self.save_directory)
    
    def to_dict(self) -> Dict:
        return {
            "game_id": self.game_id,
            "player_names": self.player_names,
            "rounds": [round.to_dict() for round in self.rounds],
            "winner": self.winner,
        }
    
    def start_game(self, player_names: List[str]) -> None:
        """Initialize game and record players"""
        self.player_names = player_names
    
    def start_round(self, round_id: int, target_card: str, round_players: List[str], 
                   starting_player: str, player_initial_states: List[PlayerInitialState], 
                   player_opinions: Dict[str, Dict[str, str]]) -> None:
        """Start new debate round"""
        round_record = RoundRecord(
            round_id=round_id,
            target_card=target_card,
            round_players=round_players,
            starting_player=starting_player,
            player_initial_states=player_initial_states,
            player_opinions=player_opinions
        )
        self.rounds.append(round_record)
    
    def record_play(self, player_name: str, played_cards: List[str], remaining_cards: List[str],
                   play_reason: str, behavior: str, next_player: str, play_thinking: str = None) -> None:
        """Record player's argument presentation"""
        current_round = self.get_current_round()
        if current_round:
            play_action = PlayAction(
                player_name=player_name,
                played_cards=played_cards,
                remaining_cards=remaining_cards,
                play_reason=play_reason,
                behavior=behavior,
                next_player=next_player,
                play_thinking=play_thinking
            )
            current_round.add_play_action(play_action)
    
    def record_challenge(self, was_challenged: bool, reason: str = None, 
                        result: bool = None, challenge_thinking: str = None) -> None:
        """Record challenge information"""
        current_round = self.get_current_round()
        if current_round:
            last_action = current_round.get_last_action()
            if last_action:
                last_action.update_challenge(was_challenged, reason, result, challenge_thinking)
                if was_challenged:
                    self.auto_save()
    
    def finish_game(self, result: str) -> None:
        """Record game conclusion and save"""
        self.winner = result
        self.auto_save()
    
    def get_current_round(self) -> Optional[RoundRecord]:
        """Get current round record"""
        return self.rounds[-1] if self.rounds else None
    
    def get_latest_round_info(self) -> Optional[str]:
        """Get latest round base information"""
        current_round = self.get_current_round()
        return current_round.get_latest_round_info() if current_round else None

    def get_latest_round_actions(self, current_player: str, include_latest: bool = True) -> Optional[str]:
        """Get latest round action information"""
        current_round = self.get_current_round()
        return current_round.get_latest_round_actions(current_player, include_latest) if current_round else None
    
    def get_latest_play_behavior(self) -> Optional[str]:
        """Get latest round's latest player behavior"""
        current_round = self.get_current_round()
        return current_round.get_latest_play_behavior() if current_round else None

    def get_latest_round_result(self, current_player: str) -> Optional[str]:
        """Get latest round result"""
        current_round = self.get_current_round()
        return current_round.get_latest_round_result(current_player) if current_round else None

    def get_play_decision_info(self, self_player: str, interacting_player: str) -> Optional[str]:
        """Get latest round play decision information"""
        current_round = self.get_current_round()
        return current_round.get_play_decision_info(self_player, interacting_player) if current_round else None

    def get_challenge_decision_info(self, self_player: str, interacting_player: str) -> Optional[str]:
        """Get latest round challenge decision information"""
        current_round = self.get_current_round()
        return current_round.get_challenge_decision_info(self_player, interacting_player) if current_round else None

    def auto_save(self) -> None:
        """Automatically save current game record"""
        file_path = os.path.join(self.save_directory, f"{self.game_id}.json")
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(self.to_dict(), file, indent=4, ensure_ascii=False)
        print(f"Debate record saved to {file_path}")
