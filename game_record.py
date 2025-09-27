from dataclasses import dataclass, field
from typing import List, Dict, Optional
import datetime
import json
import os
import time

def generate_game_id():
    """生成包含时间信息的游戏 ID"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return timestamp

@dataclass
class ModelPerformanceRecord:
    """记录模型特定的性能指标"""
    model_name: str
    player_name: str
    decision_count: int = 0
    successful_challenges: int = 0
    failed_challenges: int = 0
    successful_defenses: int = 0
    failed_defenses: int = 0
    total_response_time: float = 0.0
    human_scores: List[Dict[str, int]] = field(default_factory=list)
    
    @property
    def average_response_time(self) -> float:
        """计算平均响应时间"""
        return self.total_response_time / self.decision_count if self.decision_count > 0 else 0.0
    
    @property
    def challenge_success_rate(self) -> float:
        """计算质疑成功率"""
        total_challenges = self.successful_challenges + self.failed_challenges
        return self.successful_challenges / total_challenges if total_challenges > 0 else 0.0
    
    @property
    def defense_success_rate(self) -> float:
        """计算防守成功率"""
        total_defenses = self.successful_defenses + self.failed_defenses
        return self.successful_defenses / total_defenses if total_defenses > 0 else 0.0
    
    def to_dict(self) -> Dict:
        return {
            "model_name": self.model_name,
            "player_name": self.player_name,
            "decision_count": self.decision_count,
            "successful_challenges": self.successful_challenges,
            "failed_challenges": self.failed_challenges,
            "successful_defenses": self.successful_defenses,
            "failed_defenses": self.failed_defenses,
            "total_response_time": self.total_response_time,
            "average_response_time": self.average_response_time,
            "challenge_success_rate": self.challenge_success_rate,
            "defense_success_rate": self.defense_success_rate,
            "human_scores": self.human_scores
        }

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
    talk: str  # Player's speech during their turn
    next_player: str
    was_challenged: bool = False
    challenge_reason: Optional[str] = None
    challenge_result: Optional[bool] = None
    play_thinking: Optional[str] = None
    challenge_thinking: Optional[str] = None
    play_response_time: Optional[float] = None
    challenge_response_time: Optional[float] = None
    
    def to_dict(self) -> Dict:
        return {
            "player_name": self.player_name,
            "played_cards": self.played_cards,
            "remaining_cards": self.remaining_cards,
            "play_reason": self.play_reason,
            "behavior": self.behavior,
            "talk": self.talk,
            "next_player": self.next_player,
            "was_challenged": self.was_challenged,
            "challenge_reason": self.challenge_reason,
            "challenge_result": self.challenge_result,
            "play_thinking": self.play_thinking,
            "challenge_thinking": self.challenge_thinking,
            "play_response_time": self.play_response_time,
            "challenge_response_time": self.challenge_response_time
        }
    
    def update_challenge(self, was_challenged: bool, reason: str, result: bool, challenge_thinking: str = None, challenge_response_time: float = None) -> None:
        """更新质疑信息"""
        self.was_challenged = was_challenged
        self.challenge_reason = reason
        self.challenge_result = result
        self.challenge_thinking = challenge_thinking
        self.challenge_response_time = challenge_response_time

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
    model_assignments: Dict[str, str] = field(default_factory=dict)
    human_scores: Dict[str, Dict[str, int]] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "round_id": self.round_id,
            "target_card": self.target_card,
            "round_players": self.round_players,
            "starting_player": self.starting_player,
            "player_initial_states": [ps.to_dict() for ps in self.player_initial_states],
            "player_opinions": self.player_opinions,
            "play_history": [play.to_dict() for play in self.play_history],
            "model_assignments": self.model_assignments,
            "human_scores": self.human_scores
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
                    f"Remaining cards: {', '.join(action.remaining_cards)}\n"
                    f"Your behavior: {action.behavior}\n"
                    f"You said: \"{action.talk}\""
                )
            else:
                action_texts.append(
                    f"{action.player_name}'s turn, claimed to play {len(action.played_cards)} '{self.target_card}' cards, "
                    f"Has {len(action.remaining_cards)} cards remaining\n"
                    f"{action.player_name}'s behavior: {action.behavior}\n"
                    f"{action.player_name} said: \"{action.talk}\""
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
                f"{last_action.player_name}'s behavior: {last_action.behavior}, "
                f"Said: \"{last_action.talk}\"")
    
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
        self.player_model_assignments: Dict[str, str] = {}
        self.judge_model_assignments: Dict[str, str] = {}
        self.model_performance: Dict[str, ModelPerformanceRecord] = {}
        
        # 确保保存目录存在
        if not os.path.exists(self.save_directory):
            os.makedirs(self.save_directory)
    
    def to_dict(self) -> Dict:
        return {
            "game_id": self.game_id,
            "player_names": self.player_names,
            "rounds": [round.to_dict() for round in self.rounds],
            "winner": self.winner,
            "player_model_assignments": self.player_model_assignments,
            "judge_model_assignments": self.judge_model_assignments,
            "model_performance": {k: v.to_dict() for k, v in self.model_performance.items()},
        }
    
    def start_game(self, player_names: List[str]) -> None:
        """初始化游戏，记录玩家信息"""
        self.player_names = player_names
    
    def set_player_model_assignments(self, assignments: Dict[str, str]) -> None:
        """设置玩家模型分配"""
        self.player_model_assignments = assignments.copy()
        # Initialize model performance records
        for player_name, model_name in assignments.items():
            key = f"{player_name}_{model_name}"
            self.model_performance[key] = ModelPerformanceRecord(
                model_name=model_name,
                player_name=player_name
            )
    
    def set_judge_model_assignments(self, assignments: Dict[str, str]) -> None:
        """设置评委模型分配"""
        self.judge_model_assignments = assignments.copy()
    
    def get_player_model(self, player_name: str) -> Optional[str]:
        """获取指定玩家的模型"""
        return self.player_model_assignments.get(player_name)
    
    def get_judge_model(self, judge_name: str) -> Optional[str]:
        """获取指定评委的模型"""
        return self.judge_model_assignments.get(judge_name)
    
    def get_model_performance_key(self, player_name: str) -> Optional[str]:
        """获取模型性能记录的键"""
        model_name = self.get_player_model(player_name)
        return f"{player_name}_{model_name}" if model_name else None
    
    def start_round(self, round_id: int, target_card: str, round_players: List[str], starting_player: str, player_initial_states: List[PlayerInitialState], player_opinions: Dict[str, Dict[str, str]]) -> None:
        """开始新的一轮游戏"""
        # Create model assignments for this round's players
        round_model_assignments = {
            player: self.player_model_assignments.get(player, "unknown")
            for player in round_players
        }
        
        round_record = RoundRecord(
            round_id=round_id,
            target_card=target_card,
            round_players=round_players,
            starting_player=starting_player,
            player_initial_states=player_initial_states,
            player_opinions=player_opinions,
            model_assignments=round_model_assignments
        )
        self.rounds.append(round_record)
    
    def record_play(self, player_name: str, played_cards: List[str], remaining_cards: List[str], 
                   play_reason: str, behavior: str, talk: str, next_player: str, play_thinking: str = None, 
                   play_response_time: float = None) -> None:
        """记录玩家的出牌行为"""
        current_round = self.get_current_round()
        if current_round:
            play_action = PlayAction(
                player_name=player_name,
                played_cards=played_cards,
                remaining_cards=remaining_cards,
                play_reason=play_reason,
                behavior=behavior,
                talk=talk,
                next_player=next_player,
                play_thinking=play_thinking,
                play_response_time=play_response_time
            )
            current_round.add_play_action(play_action)
            
            # Update model performance metrics
            perf_key = self.get_model_performance_key(player_name)
            if perf_key and perf_key in self.model_performance:
                perf_record = self.model_performance[perf_key]
                perf_record.decision_count += 1
                if play_response_time:
                    perf_record.total_response_time += play_response_time
    
    def record_challenge(self, was_challenged: bool, reason: str = None, result: bool = None, 
                        challenge_thinking: str = None, challenge_response_time: float = None, 
                        challenger_name: str = None) -> None:
        """记录质疑信息"""
        current_round = self.get_current_round()
        if current_round:
            last_action = current_round.get_last_action()
            if last_action:
                last_action.update_challenge(was_challenged, reason, result, challenge_thinking, challenge_response_time)
                
                # Update model performance metrics
                if was_challenged and challenger_name and result is not None:
                    # Update challenger's performance
                    challenger_perf_key = self.get_model_performance_key(challenger_name)
                    if challenger_perf_key and challenger_perf_key in self.model_performance:
                        challenger_perf = self.model_performance[challenger_perf_key]
                        if result:  # Challenge successful
                            challenger_perf.successful_challenges += 1
                        else:  # Challenge failed
                            challenger_perf.failed_challenges += 1
                        if challenge_response_time:
                            challenger_perf.decision_count += 1
                            challenger_perf.total_response_time += challenge_response_time
                    
                    # Update defender's performance
                    defender_perf_key = self.get_model_performance_key(last_action.player_name)
                    if defender_perf_key and defender_perf_key in self.model_performance:
                        defender_perf = self.model_performance[defender_perf_key]
                        if result:  # Defense failed
                            defender_perf.failed_defenses += 1
                        else:  # Defense successful
                            defender_perf.successful_defenses += 1
    
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

    def get_model_performance_statistics(self) -> Dict[str, Dict]:
        """获取所有模型的性能统计"""
        stats = {}
        for key, perf_record in self.model_performance.items():
            stats[key] = {
                "model_name": perf_record.model_name,
                "player_name": perf_record.player_name,
                "decision_count": perf_record.decision_count,
                "average_response_time": perf_record.average_response_time,
                "challenge_success_rate": perf_record.challenge_success_rate,
                "defense_success_rate": perf_record.defense_success_rate,
                "successful_challenges": perf_record.successful_challenges,
                "failed_challenges": perf_record.failed_challenges,
                "successful_defenses": perf_record.successful_defenses,
                "failed_defenses": perf_record.failed_defenses
            }
        return stats
    
    def get_model_comparison_report(self) -> Dict[str, Dict]:
        """生成模型对比报告"""
        model_stats = {}
        
        # Group performance by model name
        for perf_record in self.model_performance.values():
            model_name = perf_record.model_name
            if model_name not in model_stats:
                model_stats[model_name] = {
                    "total_decisions": 0,
                    "total_response_time": 0.0,
                    "total_successful_challenges": 0,
                    "total_failed_challenges": 0,
                    "total_successful_defenses": 0,
                    "total_failed_defenses": 0,
                    "players": []
                }
            
            stats = model_stats[model_name]
            stats["total_decisions"] += perf_record.decision_count
            stats["total_response_time"] += perf_record.total_response_time
            stats["total_successful_challenges"] += perf_record.successful_challenges
            stats["total_failed_challenges"] += perf_record.failed_challenges
            stats["total_successful_defenses"] += perf_record.successful_defenses
            stats["total_failed_defenses"] += perf_record.failed_defenses
            stats["players"].append(perf_record.player_name)
        
        # Calculate aggregated metrics
        for model_name, stats in model_stats.items():
            total_challenges = stats["total_successful_challenges"] + stats["total_failed_challenges"]
            total_defenses = stats["total_successful_defenses"] + stats["total_failed_defenses"]
            
            stats["average_response_time"] = (
                stats["total_response_time"] / stats["total_decisions"] 
                if stats["total_decisions"] > 0 else 0.0
            )
            stats["challenge_success_rate"] = (
                stats["total_successful_challenges"] / total_challenges 
                if total_challenges > 0 else 0.0
            )
            stats["defense_success_rate"] = (
                stats["total_successful_defenses"] / total_defenses 
                if total_defenses > 0 else 0.0
            )
        
        return model_stats
    
    def add_human_scores_to_model(self, player_name: str, scores: Dict[str, int]) -> None:
        """为指定玩家的模型添加人类评分"""
        perf_key = self.get_model_performance_key(player_name)
        if perf_key and perf_key in self.model_performance:
            self.model_performance[perf_key].human_scores.append(scores)
    
    def add_human_scores_to_latest_round(self, human_scores: Dict[str, Dict[str, int]]) -> None:
        """为最新轮次添加人类评分"""
        current_round = self.get_current_round()
        if current_round and hasattr(current_round, 'human_scores'):
            # Add to round record if it has human_scores field
            if not hasattr(current_round, 'human_scores'):
                current_round.human_scores = {}
            current_round.human_scores.update(human_scores)
        
        # Also add to model performance records
        for player_name, scores in human_scores.items():
            self.add_human_scores_to_model(player_name, scores)
    
    def get_game_session_analytics(self) -> Dict[str, Any]:
        """获取游戏会话分析数据"""
        return {
            "game_id": self.game_id,
            "winner": self.winner,
            "total_rounds": len(self.rounds),
            "total_decisions": sum(perf.decision_count for perf in self.model_performance.values()),
            "player_model_assignments": self.player_model_assignments.copy(),
            "judge_model_assignments": self.judge_model_assignments.copy(),
            "model_performance_summary": self.get_model_performance_statistics(),
            "human_scoring_data": self._extract_human_scoring_data()
        }
    
    def _extract_human_scoring_data(self) -> Dict[str, Any]:
        """提取人类评分数据"""
        human_scoring_data = {
            "total_human_scores": 0,
            "models_with_human_scores": [],
            "average_human_scores_by_model": {}
        }
        
        for perf_key, perf_record in self.model_performance.items():
            if perf_record.human_scores:
                human_scoring_data["total_human_scores"] += len(perf_record.human_scores)
                human_scoring_data["models_with_human_scores"].append(perf_record.model_name)
                
                # Calculate average human score for this model
                all_scores = []
                for score_dict in perf_record.human_scores:
                    if isinstance(score_dict, dict):
                        all_scores.extend(score_dict.values())
                
                if all_scores:
                    avg_score = sum(all_scores) / len(all_scores)
                    human_scoring_data["average_human_scores_by_model"][perf_record.model_name] = avg_score
        
        return human_scoring_data

    def auto_save(self) -> None:
        """自动保存当前游戏记录到文件"""
        file_path = os.path.join(self.save_directory, f"{self.game_id}.json")
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(self.to_dict(), file, indent=4, ensure_ascii=False)
        print(f"Game record auto-saved to {file_path}")
