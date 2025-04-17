from dataclasses import dataclass, field
from typing import List, Dict, Optional
import datetime
import json
import os

def generate_game_id():
    """生成包含时间信息的游戏 ID"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return timestamp

@dataclass
class PlayerInitialState:
    """记录玩家初始状态和手牌"""
    player_name: str
    initial_hand: List[str]
    
    def to_dict(self) -> Dict:
        return {
            "player_name": self.player_name,
            "initial_hand": self.initial_hand
        }

@dataclass
class PlayAction:
    """记录一次出牌行为"""
    player_name: str
    played_cards: List[str]
    remaining_cards: List[str]
    play_reason: str
    behavior: str
    next_player: str
    was_challenged: bool = False
    challenge_reason: Optional[str] = None
    challenge_result: Optional[bool] = None
    play_thinking: Optional[str] = None
    challenge_thinking: Optional[str] = None
    
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
        """更新质疑信息"""
        self.was_challenged = was_challenged
        self.challenge_reason = reason
        self.challenge_result = result
        self.challenge_thinking = challenge_thinking

@dataclass
class RoundRecord:
    """记录一轮游戏"""
    round_id: int
    target_card: str
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
        """添加出牌记录"""
        self.play_history.append(action)
    
    def get_last_action(self) -> Optional[PlayAction]:
        """获取最后一次出牌记录"""
        return self.play_history[-1] if self.play_history else None
    
    def get_latest_round_info(self) -> str:
        """返回最新轮次的基础信息"""
        return (
            f"Current round: {self.round_id}, Target card: {self.target_card}, Players: {', '.join(self.round_players)}, "
            f"Starting with player {self.starting_player}"
        )

    def get_latest_round_actions(self, current_player: str, include_latest: bool = True) -> str:
        """
        输入当前玩家，返回该轮次的操作信息
        
        Args:
            current_player (str): 当前玩家名称
            include_latest (bool): 是否包含最新一次操作，默认为 True
        
        Returns:
            str: 格式化的操作信息文本
        """
        action_texts = []
        actions_to_process = self.play_history if include_latest else self.play_history[:-1]
        
        for action in actions_to_process:
            if action.player_name == current_player:
                action_texts.append(
                    f"Your turn, you played {len(action.played_cards)} cards: {', '.join(action.played_cards)}, "
                    f"Remaining cards: {', '.join(action.remaining_cards)}\nYour behavior: {action.behavior}"
                )
            else:
                action_texts.append(
                    f"{action.player_name}'s turn, claimed to play {len(action.played_cards)} '{self.target_card}' cards, "
                    f"Has {len(action.remaining_cards)} cards remaining\n{action.player_name}'s behavior: {action.behavior}"
                )
            
            if action.was_challenged:
                actual_cards = f"Cards played were: {', '.join(action.played_cards)}"
                challenge_result_text = f"{actual_cards}, challenge successful" if action.challenge_result else f"{actual_cards}, challenge failed"
                if action.next_player == current_player:
                    challenge_text = f"You chose to challenge {action.player_name}, {action.player_name} {challenge_result_text}"
                elif action.player_name == current_player:
                    challenge_text = f"{action.next_player} challenged you, you {challenge_result_text}"
                else:
                    challenge_text = f"{action.next_player} challenged {action.player_name}, {action.player_name} {challenge_result_text}"
            else:
                if action.next_player == current_player:
                    challenge_text = f"You chose not to challenge {action.player_name}"
                elif action.player_name == current_player:
                    challenge_text = f"{action.next_player} chose not to challenge you"
                else:
                    challenge_text = f"{action.next_player} chose not to challenge {action.player_name}"
            action_texts.append(challenge_text)
        
        return "\n".join(action_texts)
    
    def get_latest_play_behavior(self) -> str:
        """
        获取最新玩家的出牌表现
        
        Returns:
            str: 格式化的出牌行为描述
        """
        if not self.play_history:
            return ""
            
        last_action = self.get_last_action()
        if not last_action:
            return ""
            
        return (f"{last_action.player_name} claimed to play {len(last_action.played_cards)} '{self.target_card}' cards, "
                f"Has {len(last_action.remaining_cards)} cards remaining, "
                f"{last_action.player_name}'s behavior: {last_action.behavior}")
    
    def get_play_decision_info(self, self_player: str, interacting_player: str) -> str:
        """获取当前轮次出牌决策相关信息
        
        Args:
            self_player: 当前玩家
            interacting_player: 下家玩家
        Returns:
            str: 包含玩家印象信息
        """
        opinion = self.player_opinions[self_player].get(interacting_player, "Don't know this player yet")
        return (f"{interacting_player} is next player, deciding whether to challenge your play.\n"
                f"Your analysis of {interacting_player}: {opinion}")

    def get_challenge_decision_info(self, self_player: str, interacting_player: str) -> str:
        """获取当前轮次质疑决策相关信息
        
        Args:
            self_player: 当前玩家
            interacting_player: 上家玩家
        Returns:
            str: 包含玩家印象信息
        """
        opinion = self.player_opinions[self_player].get(interacting_player, "Don't know this player yet")
        return (f"You are deciding whether to challenge {interacting_player}'s play.\n"
                f"Your analysis of {interacting_player}: {opinion}")

@dataclass
class GameRecord:
    """完整游戏记录"""
    def __init__(self):
        self.game_id: str = generate_game_id()
        self.player_names: List[str] = []
        self.rounds: List[RoundRecord] = []
        self.winner: Optional[str] = None
        self.save_directory: str = "game_records"
        
        # 确保保存目录存在
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
        """初始化游戏，记录玩家信息"""
        self.player_names = player_names
    
    def start_round(self, round_id: int, target_card: str, round_players: List[str], starting_player: str, player_initial_states: List[PlayerInitialState], player_opinions: Dict[str, Dict[str, str]]) -> None:
        """开始新的一轮游戏"""
        round_record = RoundRecord(
            round_id=round_id,
            target_card=target_card,
            round_players=round_players,
            starting_player=starting_player,
            player_initial_states=player_initial_states,
            player_opinions=player_opinions
        )
        self.rounds.append(round_record)
    
    def record_play(self, player_name: str, played_cards: List[str], remaining_cards: List[str], play_reason: str, behavior: str, next_player: str, play_thinking: str = None) -> None:
        """记录玩家的出牌行为"""
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
    
    def record_challenge(self, was_challenged: bool, reason: str = None, result: bool = None, challenge_thinking: str = None) -> None:
        """记录质疑信息"""
        current_round = self.get_current_round()
        if current_round:
            last_action = current_round.get_last_action()
            if last_action:
                last_action.update_challenge(was_challenged, reason, result, challenge_thinking)
    
    def finish_game(self, winner_name: str) -> None:
        """记录胜利者并保存最终结果"""
        self.winner = winner_name
        self.auto_save()  # 游戏结束时保存
    
    def get_current_round(self) -> Optional[RoundRecord]:
        """获取当前轮次"""
        return self.rounds[-1] if self.rounds else None
    
    def get_latest_round_info(self) -> Optional[str]:
        """获取最新轮次基础信息"""
        current_round = self.get_current_round()
        return current_round.get_latest_round_info() if current_round else None

    def get_latest_round_actions(self, current_player: str, include_latest: bool = True) -> Optional[str]:
        """获取最新轮次的操作信息"""
        current_round = self.get_current_round()
        return current_round.get_latest_round_actions(current_player, include_latest) if current_round else None
    
    def get_latest_play_behavior(self) -> Optional[str]:
        """
        获取最新轮次中最新玩家的出牌表现
        """
        current_round = self.get_current_round()
        return current_round.get_latest_play_behavior() if current_round else None

    def get_play_decision_info(self, self_player: str, interacting_player: str) -> Optional[str]:
        """获取最新轮次出牌决策相关信息
        """
        current_round = self.get_current_round()
        return current_round.get_play_decision_info(self_player, interacting_player) if current_round else None

    def get_challenge_decision_info(self, self_player: str, interacting_player: str) -> Optional[str]:
        """获取最新轮次质疑决策相关信息
        """
        current_round = self.get_current_round()
        return current_round.get_challenge_decision_info(self_player, interacting_player) if current_round else None

    def auto_save(self) -> None:
        """自动保存当前游戏记录到文件"""
        file_path = os.path.join(self.save_directory, f"{self.game_id}.json")
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(self.to_dict(), file, indent=4, ensure_ascii=False)
        print(f"Game record auto-saved to {file_path}")
