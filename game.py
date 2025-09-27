import random
from typing import List, Optional, Dict
from player import Player
from game_record import GameRecord, PlayerInitialState
from judge_panel import JudgePanel
from model_config_manager import ModelConfigManager
from human_scoring_interface import HumanScoringInterface
from game_analytics_integration import GameAnalyticsManager

class Game:
    def __init__(self, player_configs: List[Dict[str, str]], judge_configs: List[Dict[str, str]], 
                 model_config_manager: Optional[ModelConfigManager] = None,
                 enable_human_scoring: bool = False,
                 human_scoring_port: int = 5001,
                 enable_analytics: bool = True) -> None:
        """初始化游戏
        
        Args:
            player_configs: 包含玩家配置的列表，每个配置是一个字典，包含 name 和 model 字段
            judge_configs: 包含裁判配置的列表，每个配置是一个字典，包含 name 和 model 字段
            model_config_manager: 可选的模型配置管理器，用于验证模型配置
            enable_human_scoring: 是否启用人工评分功能
            human_scoring_port: 人工评分界面的端口号
        """
        # Validate model configurations if manager is provided
        if model_config_manager:
            self._validate_configurations(player_configs, judge_configs, model_config_manager)
        
        # Get error handling components from model config manager
        failure_handler = None
        degradation_manager = None
        if model_config_manager:
            failure_handler = model_config_manager.get_failure_handler()
            degradation_manager = model_config_manager.get_degradation_manager()
        
        # 使用配置创建玩家对象，包含错误处理组件
        self.players = [
            Player(
                config["name"], 
                config["model"],
                failure_handler=failure_handler,
                degradation_manager=degradation_manager
            ) 
            for config in player_configs
        ]
        
        # 初始化每个玩家对其他玩家的看法
        for player in self.players:
            player.init_opinions(self.players)
        
        self.deck: List[str] = []
        self.target_card: Optional[str] = None
        self.current_player_idx: int = random.randint(0, len(self.players) - 1)
        self.game_over: bool = False

        # Initialize judge panel with human scoring capability
        self.judge_panel = JudgePanel(judge_configs)
        
        # Initialize human scoring interface if enabled
        self.enable_human_scoring = enable_human_scoring
        self.human_scoring_interface: Optional[HumanScoringInterface] = None
        if enable_human_scoring:
            self.human_scoring_interface = HumanScoringInterface(human_scoring_port)
            self.judge_panel.set_human_scoring_interface(self.human_scoring_interface)
        
        # Store model config manager reference
        self.model_config_manager = model_config_manager
        
        # 创建游戏记录
        self.game_record: GameRecord = GameRecord()
        self.game_record.start_game([p.name for p in self.players])
        self.round_count = 0
        
        # Set up model assignments in game record
        player_model_assignments = {config["name"]: config["model"] for config in player_configs}
        judge_model_assignments = {config["name"]: config["model"] for config in judge_configs}
        self.game_record.set_player_model_assignments(player_model_assignments)
        self.game_record.set_judge_model_assignments(judge_model_assignments)
        
        # Initialize analytics integration
        self.enable_analytics = enable_analytics
        self.analytics_manager: Optional[GameAnalyticsManager] = None
        if enable_analytics:
            self.analytics_manager = GameAnalyticsManager()
        
        # Initialize player scores
        self.judge_panel.initialize_scores([p.name for p in self.players])

    def _validate_configurations(self, player_configs: List[Dict[str, str]], 
                                judge_configs: List[Dict[str, str]], 
                                model_config_manager: ModelConfigManager) -> None:
        """验证玩家和裁判的模型配置
        
        Args:
            player_configs: 玩家配置列表
            judge_configs: 裁判配置列表
            model_config_manager: 模型配置管理器
            
        Raises:
            ValueError: 如果配置无效
        """
        print("Validating model configurations...")
        
        # Collect all unique models to validate
        models_to_validate = set()
        
        # Validate player configurations
        for i, config in enumerate(player_configs):
            if "name" not in config or "model" not in config:
                raise ValueError(f"Player config {i} missing required 'name' or 'model' field")
            models_to_validate.add(config["model"])
        
        # Validate judge configurations
        for i, config in enumerate(judge_configs):
            if "name" not in config or "model" not in config:
                raise ValueError(f"Judge config {i} missing required 'name' or 'model' field")
            models_to_validate.add(config["model"])
        
        # Validate each unique model
        invalid_models = []
        for model in models_to_validate:
            if not model_config_manager.validate_model(model):
                invalid_models.append(model)
        
        if invalid_models:
            raise ValueError(f"Invalid or unavailable models: {', '.join(invalid_models)}")
        
        print(f"✓ All models validated successfully: {', '.join(models_to_validate)}")

    def _record_human_scores(self, human_scores: Dict[str, Dict[str, int]]) -> None:
        """记录人工评分到游戏记录中
        
        Args:
            human_scores: 人工评分数据，格式为 {player_name: {criterion: score}}
        """
        try:
            # Add human scores to the latest round record
            if hasattr(self.game_record, 'add_human_scores_to_latest_round'):
                self.game_record.add_human_scores_to_latest_round(human_scores)
            else:
                # Fallback: store in a simple format for now
                print(f"Human scores recorded for round {self.round_count}")
                for player_name, scores in human_scores.items():
                    avg_score = sum(scores.values()) / len(scores) if scores else 0
                    print(f"  {player_name}: {avg_score:.1f}/5 average")
        except Exception as e:
            print(f"Warning: Could not record human scores: {e}")

    def _display_final_statistics(self) -> None:
        """显示最终游戏统计信息"""
        print("\n" + "="*60)
        print("FINAL GAME STATISTICS")
        print("="*60)
        
        # Display final AI judge scores
        print("\nFinal AI Judge Scores:")
        print("-" * 30)
        print(self.judge_panel.get_score_summary())
        
        # Display human scoring statistics if available
        if self.enable_human_scoring and self.human_scoring_interface:
            stats = self.human_scoring_interface.get_scoring_statistics()
            print("\nHuman Scoring Statistics:")
            print("-" * 30)
            print(f"Total scoring sessions: {stats['total_sessions']}")
            print(f"Completed sessions: {stats['completed_sessions']}")
            print(f"Timeout sessions: {stats['timeout_sessions']}")
            if stats['average_scoring_time'] > 0:
                print(f"Average scoring time: {stats['average_scoring_time']:.1f} seconds")
        
        # Display model assignments for reference
        print("\nModel Assignments:")
        print("-" * 30)
        print("Players:")
        for player in self.players:
            print(f"  {player.name} -> {player.model_name}")
        
        print("Judges:")
        for judge in self.judge_panel.judges:
            print(f"  {judge['name']} -> {judge['model']}")
        
        # Generate and display analytics report if enabled
        if self.enable_analytics and self.analytics_manager:
            try:
                # Get final scores from judge panel
                final_scores = {}
                for player in self.players:
                    # This would need to be implemented in judge_panel to get actual scores
                    final_scores[player.name] = 0  # Placeholder
                
                # Generate post-game report
                self.analytics_manager.generate_post_game_report(
                    self.game_record,
                    display_report=True,
                    export_formats=["json"]  # Auto-export as JSON
                )
            except Exception as e:
                print(f"Analytics report generation failed: {e}")
        
        print("="*60)
    
    def _display_error_statistics(self) -> None:
        """显示错误处理统计信息"""
        try:
            error_stats = self.model_config_manager.get_error_statistics()
            
            # Display failure statistics
            failure_stats = error_stats.get("failure_statistics", {})
            if any(failure_stats.values()):
                print("\nModel Failure Statistics:")
                print("-" * 30)
                
                failure_counts = failure_stats.get("failure_counts", {})
                consecutive_failures = failure_stats.get("consecutive_failures", {})
                
                for model, count in failure_counts.items():
                    if count > 0:
                        consecutive = consecutive_failures.get(model, 0)
                        print(f"  {model}: {count} total failures, {consecutive} consecutive")
            
            # Display degradation status
            degradation_status = error_stats.get("degradation_status", {})
            degraded_players = degradation_status.get("degraded_players", {})
            timeout_counts = degradation_status.get("timeout_counts", {})
            
            if degraded_players or timeout_counts:
                print("\nPlayer Degradation Status:")
                print("-" * 30)
                
                for player, reason in degraded_players.items():
                    print(f"  {player}: {reason}")
                
                for player, count in timeout_counts.items():
                    if count > 0:
                        print(f"  {player}: {count} timeouts")
            
            # Display model performance report if available
            degradation_manager = self.model_config_manager.get_degradation_manager()
            performance_report = degradation_manager.get_model_performance_report()
            
            if performance_report:
                print("\nModel Performance Report:")
                print("-" * 30)
                for model, stats in performance_report.items():
                    print(f"  {model}:")
                    print(f"    Success Rate: {stats['success_rate']}")
                    print(f"    Timeout Rate: {stats['timeout_rate']}")
                    print(f"    Average Response Time: {stats['average_response_time']}")
                    
        except Exception as e:
            print(f"\nError displaying statistics: {e}")

    @classmethod
    def create_from_preset(cls, preset_name: str, model_config_manager: ModelConfigManager, 
                          enable_human_scoring: bool = False, human_scoring_port: int = 5001):
        """从预设配置创建游戏实例
        
        Args:
            preset_name: 预设配置名称
            model_config_manager: 模型配置管理器
            enable_human_scoring: 是否启用人工评分
            human_scoring_port: 人工评分界面端口
            
        Returns:
            Game: 配置好的游戏实例
            
        Raises:
            ValueError: 如果预设无效或模型不可用
        """
        try:
            # Load preset configuration
            preset_config = model_config_manager.load_preset(preset_name)
            
            # Validate all models in the preset
            validation_results = model_config_manager.validate_preset_models(preset_name)
            invalid_models = [model for model, is_valid in validation_results.items() if not is_valid]
            
            if invalid_models:
                raise ValueError(f"Invalid models in preset '{preset_name}': {', '.join(invalid_models)}")
            
            # Extract configurations
            player_configs = preset_config["player_configs"]
            judge_configs = preset_config["judge_configs"]
            
            print(f"Creating game from preset: {preset_name}")
            print(f"Description: {preset_config.get('description', 'No description')}")
            
            # Create game instance
            return cls(
                player_configs=player_configs,
                judge_configs=judge_configs,
                model_config_manager=model_config_manager,
                enable_human_scoring=enable_human_scoring,
                human_scoring_port=human_scoring_port
            )
            
        except Exception as e:
            raise ValueError(f"Failed to create game from preset '{preset_name}': {str(e)}")

    def _create_deck(self) -> List[str]:
        """创建空牌组"""
        return []

    def deal_cards(self) -> None:
        """给每个存活玩家5张K牌"""
        self.deck = self._create_deck()
        for player in self.players:
            if player.alive:
                player.hand.clear()
                player.hand = ['K'] * 5
                player.print_status()

    def choose_target_card(self) -> None:
        """随机选择目标牌"""
        self.target_card = random.choice(['Q', 'K', 'A'])
        print(f"Target card is: {self.target_card}")

    def start_round_record(self) -> None:
        """开始新的回合，并在 `GameRecord` 里记录信息"""
        self.round_count += 1
        starting_player = self.players[self.current_player_idx].name
        player_initial_states = [
            PlayerInitialState(
                player_name=player.name,
                initial_hand=player.hand.copy()
            )
            for player in self.players if player.alive
        ]

        # 获取当前存活的玩家
        round_players = [player.name for player in self.players if player.alive]

        # 创建一个深拷贝，而不是引用
        player_opinions = {}
        for player in self.players:
            player_opinions[player.name] = {}
            for target, opinion in player.opinions.items():
                player_opinions[player.name][target] = opinion

        self.game_record.start_round(
            round_id=self.round_count,
            target_card=self.target_card,
            round_players=round_players,
            starting_player=starting_player,
            player_initial_states=player_initial_states,
            player_opinions=player_opinions
        )

    def is_valid_play(self, cards: List[str]) -> bool:
        """
        判断出牌是否符合目标牌规则：
        每张牌必须为目标牌或 Joker
        """
        return all(card == self.target_card or card == 'Joker' for card in cards)

    def find_next_player_with_cards(self, start_idx: int) -> int:
        """返回下一个存活且有手牌的玩家索引"""
        idx = start_idx
        for _ in range(len(self.players)):
            idx = (idx + 1) % len(self.players)
            if self.players[idx].alive and self.players[idx].hand:
                return idx
        return start_idx  # 理论上不会发生

    def reset_round(self, use_current_player: bool) -> None:
        """重置当前小局
        
        Args:
            use_current_player: 是否使用当前玩家作为下一轮的开始者
        """
        print("Round reset, starting a new round!")

        # Get round info for judges
        round_info = {
            "base_info": self.game_record.get_latest_round_info(),
            "action_info": self.game_record.get_latest_round_actions(None, include_latest=True),
            "round_id": self.round_count,
            "target_card": self.target_card,
            "round_players": [p.name for p in self.players if p.alive]
        }

        # Evaluate round with both AI judges and human scoring if enabled
        if self.enable_human_scoring and self.human_scoring_interface:
            # Use combined evaluation with human scoring
            combined_results = self.judge_panel.evaluate_round_with_human_input(round_info)
            
            # Display comprehensive results
            self.judge_panel.display_combined_round_summary(round_info)
            
            # Update game record with human scores if available
            human_scores = combined_results.get('human_scores', {})
            if human_scores:
                self._record_human_scores(human_scores)
            
            # Show AI judge votes for consistency
            ai_results = combined_results.get('ai_evaluation', {})
            if ai_results.get('votes'):
                print("\nAI Judge Votes Summary:")
                for judge_name, vote in ai_results["votes"].items():
                    judge_model = vote.get('judge_model', 'Unknown')
                    print(f"  {judge_name} ({judge_model}) voted for {vote['voted_player']}")
        else:
            # Standard AI-only evaluation
            self.judge_panel.evaluate_round(round_info)
            
            # Reveal votes and update scores
            vote_results = self.judge_panel.reveal_votes()
            print("\nJudge Votes:")
            for judge_name, vote in vote_results["votes"].items():
                judge_model = vote.get('judge_model', 'Unknown')
                print(f"{judge_name} ({judge_model}) voted for {vote['voted_player']}: {vote['reasoning']}")
        
        print(self.judge_panel.get_score_summary())
        
        # 在发新牌之前进行反思，并获取存活玩家列表
        alive_players = self.handle_reflection()

        # 重新发牌
        self.deal_cards()
        self.choose_target_card()
        
        # 如果不使用当前玩家，则随机选择一个存活玩家开始新一轮
        if not use_current_player:
            self.current_player_idx = self.players.index(random.choice(alive_players))

        self.start_round_record()
        print(f"New round starting with {self.players[self.current_player_idx].name}!")

    def check_victory(self) -> bool:
        """
        检查胜利条件（当前轮所有玩家出完手牌），并记录胜利者
        
        Returns:
            bool: 游戏是否结束
        """
        # 检查所有玩家是否都没有手牌
        if all(not p.hand for p in self.players):
            # 进行最终轮次评估（包括人工评分如果启用）
            final_round_info = {
                "base_info": self.game_record.get_latest_round_info(),
                "action_info": self.game_record.get_latest_round_actions(None, include_latest=True),
                "round_id": self.round_count,
                "target_card": self.target_card,
                "round_players": [p.name for p in self.players if p.alive]
            }
            
            if self.enable_human_scoring and self.human_scoring_interface:
                print("\n" + "="*60)
                print("FINAL ROUND EVALUATION")
                print("="*60)
                combined_results = self.judge_panel.evaluate_round_with_human_input(final_round_info)
                self.judge_panel.display_combined_round_summary(final_round_info)
                
                # Record human scores for final round
                human_scores = combined_results.get('human_scores', {})
                if human_scores:
                    self._record_human_scores(human_scores)
            else:
                # Standard AI-only final evaluation
                self.judge_panel.reveal_votes()
            
            winner_name = self.judge_panel.get_highest_scorer()
            print(f"\n🏆 {winner_name} has won the game!")
            
            # Display final game statistics
            self._display_final_statistics()
            
            # Display error handling statistics if available
            if self.model_config_manager:
                self._display_error_statistics()
            
            # 记录胜利者并保存游戏记录
            self.game_record.finish_game(winner_name)
            self.game_over = True
            return True
        return False
    
    def check_other_players_no_cards(self, current_player: Player) -> bool:
        """
        检查是否所有其他存活玩家都没有手牌
        """
        others = [p for p in self.players if p != current_player and p.alive]
        return all(not p.hand for p in others)

    def handle_play_cards(self, current_player: Player, next_player: Player) -> List[str]:
        """
        处理玩家出牌环节
        
        Args:
            current_player: 当前玩家
            next_player: 下一个玩家
            
        Returns:
            List[str]: 返回打出的牌组
        """
        # 获取当前轮次的基础信息
        round_base_info = self.game_record.get_latest_round_info()
        round_action_info = self.game_record.get_latest_round_actions(current_player.name, include_latest=True)
        
        # 获取出牌决策相关信息
        play_decision_info = self.game_record.get_play_decision_info(
            current_player.name,
            next_player.name
        )

        # 让当前玩家选择出牌
        play_result, reasoning = current_player.choose_cards_to_play(
            round_base_info,
            round_action_info,
            play_decision_info
        )

        # 记录出牌行为
        self.game_record.record_play(
            player_name=current_player.name,
            played_cards=play_result["played_cards"].copy(),
            remaining_cards=current_player.hand.copy(),
            play_reason=play_result["play_reason"],
            behavior=play_result["behavior"],
            talk=play_result["talk"],
            next_player=next_player.name,
            play_thinking=reasoning
        )

        return play_result["played_cards"]
    
    def handle_challenge(self, current_player: Player, next_player: Player, played_cards: List[str]) -> Player:
        """
        处理玩家质疑环节
        
        Args:
            current_player: 当前玩家（被质疑者）
            next_player: 下一个玩家（质疑者）
            played_cards: 被质疑者打出的牌
            
        Returns:
            Player: 返回需要执行惩罚的玩家
        """
        # 获取当前轮次的基础信息
        round_base_info = self.game_record.get_latest_round_info()
        round_action_info = self.game_record.get_latest_round_actions(next_player.name, include_latest=False)
        
        # 获取质疑决策相关信息
        challenge_decision_info = self.game_record.get_challenge_decision_info(
            next_player.name,
            current_player.name
        )

        # 获取被质疑玩家的表现
        challenged_player_behavior = self.game_record.get_latest_play_behavior()

        # 检查是否需要添加额外提示
        extra_hint = "Note: All other players have no cards left." if self.check_other_players_no_cards(next_player) else ""

        # 让下一位玩家决定是否质疑
        challenge_result, reasoning = next_player.decide_challenge(
            round_base_info,
            round_action_info,
            challenge_decision_info,
            challenged_player_behavior,
            extra_hint
        )

        # 如果选择质疑
        if challenge_result["was_challenged"]:
            # 验证出牌是否合法
            is_valid = self.is_valid_play(played_cards)
            
            # 记录质疑结果
            self.game_record.record_challenge(
                was_challenged=True,
                reason=challenge_result["challenge_reason"],
                result=not is_valid,  # 质疑成功意味着出牌不合法
                challenge_thinking=reasoning
            )
            
            # 根据验证结果返回需要受罚的玩家
            return next_player if is_valid else current_player
        else:
            # 记录未质疑的情况
            self.game_record.record_challenge(
                was_challenged=False,
                reason=challenge_result["challenge_reason"],
                result=None,
                challenge_thinking=reasoning
            )
            return None

    def handle_system_challenge(self, current_player: Player) -> None:
        """
        处理系统自动质疑的情况
        当其他所有存活玩家都没有手牌时，系统自动对当前玩家进行质疑
        
        Args:
            current_player: 当前玩家（最后一个有手牌的玩家）
        """
        print(f"System automatically challenging {current_player.name}'s cards!")
        
        # 记录玩家自动出牌
        all_cards = current_player.hand.copy()  # 复制当前手牌以供记录
        current_player.hand.clear()  # 清空手牌
        
        # 记录出牌行为
        self.game_record.record_play(
            player_name=current_player.name,
            played_cards=all_cards,
            remaining_cards=[],  # 剩余手牌为空列表
            play_reason="Last player, automatic play",
            behavior="none",
            talk="",
            next_player="none",
            play_thinking=""
        )
        
        # 验证出牌是否合法
        is_valid = self.is_valid_play(all_cards)
        
        # 记录系统质疑
        self.game_record.record_challenge(
            was_challenged=True,
            reason="System automatic challenge",
            result=not is_valid,  # 质疑成功意味着出牌不合法
            challenge_thinking=""
        )
        
        print(f"System challenge {'failed' if is_valid else 'successful'}! {current_player.name}'s cards {'follow' if is_valid else 'violate'} the rules.")
        self.reset_round(False)

    def handle_reflection(self) -> None:
        """
        处理所有存活玩家的反思过程
        在每轮结束时调用，让玩家对其他玩家的行为进行反思和评估
        """
        # 获取所有存活玩家
        alive_players = [p for p in self.players if p.alive]
        alive_player_names = [p.name for p in alive_players]
        
        # 获取当前轮次的相关信息
        round_base_info = self.game_record.get_latest_round_info()
        
        # 让每个存活的玩家进行反思
        for player in alive_players:
            # 获取针对当前玩家的轮次行动信息
            round_action_info = self.game_record.get_latest_round_actions(player.name, include_latest=True)
            # 执行反思
            player.reflect(
                alive_players=alive_player_names,
                round_base_info=round_base_info,
                round_action_info=round_action_info
            )

        return alive_players

    def play_round(self) -> None:
        """执行一轮游戏逻辑"""
        current_player = self.players[self.current_player_idx]

         # 当其他所有存活玩家都没有手牌时，系统自动对当前玩家进行质疑
        if self.check_other_players_no_cards(current_player):
            self.handle_system_challenge(current_player)
            return

        print(f"\nIt's {current_player.name} ({current_player.model_name})'s turn to play, target card is {self.target_card}")
        current_player.print_status()

        # 找到下一位有手牌的玩家
        next_idx = self.find_next_player_with_cards(self.current_player_idx)
        next_player = self.players[next_idx]

        # 处理出牌环节
        played_cards = self.handle_play_cards(current_player, next_player)

        # 处理质疑环节
        if next_player != current_player:
            player_to_penalize = self.handle_challenge(current_player, next_player, played_cards)
            if player_to_penalize:
                print(f"{player_to_penalize.name} played invalid cards!")
                self.reset_round(False)
                return
            else:
                print(f"{next_player.name} chose not to challenge, game continues.")
                
        # 切换至下一玩家
        self.current_player_idx = next_idx

    def _check_game_continuation(self) -> bool:
        """检查游戏是否应该继续，考虑模型失败情况"""
        if not self.model_config_manager:
            return True  # No error handling available, continue normally
        
        degradation_manager = self.model_config_manager.get_degradation_manager()
        degraded_players = list(degradation_manager.degraded_players.keys())
        
        # Check if too many players have failed
        should_continue = degradation_manager.should_continue_game(
            degraded_players, len(self.players)
        )
        
        if degraded_players:
            continuation_message = degradation_manager.generate_game_continuation_message(degraded_players)
            print(f"\n📊 Game Status: {continuation_message}")
        
        if not should_continue:
            print("\n⚠️  Too many players have experienced model failures. Ending game early.")
            return False
        
        return True
    
    def start_game(self) -> None:
        """启动游戏主循环"""
        print("\nGame Setup Complete!")
        print("Player Model Assignments:")
        for player in self.players:
            print(f"  {player.name} -> {player.model_name}")
        print()
        
        # Start analytics tracking if enabled
        if self.enable_analytics and self.analytics_manager:
            self.analytics_manager.start_game_session(self.game_record)
        
        self.deal_cards()
        self.choose_target_card()
        self.start_round_record()
        
        while not self.game_over:
            # Check if game should continue based on model failures
            if not self._check_game_continuation():
                print("\nGame ended due to excessive model failures.")
                break
            
            # Update analytics progress if enabled
            if self.enable_analytics and self.analytics_manager:
                self.analytics_manager.update_session_progress(self.game_record)
                
            self.play_round()
        
        # End analytics tracking if enabled
        if self.enable_analytics and self.analytics_manager:
            try:
                # Get final scores (placeholder implementation)
                final_scores = {player.name: 0 for player in self.players}
                self.analytics_manager.end_game_session(self.game_record, final_scores)
            except Exception as e:
                print(f"Analytics session end failed: {e}")

if __name__ == '__main__':
    from llm_client import LLMClient
    
    # Example usage demonstrating the new ModelConfigManager integration
    print("Multi-LLM Debate Game with Enhanced Configuration")
    print("=" * 60)
    
    # Initialize LLM client and model config manager
    llm_client = LLMClient()
    model_manager = ModelConfigManager(llm_client)
    
    # Option 1: Create game from preset
    try:
        print("\nOption 1: Creating game from preset...")
        available_presets = model_manager.list_presets()
        print(f"Available presets: {available_presets}")
        
        if "single_model_test" in available_presets:
            print("Using 'single_model_test' preset...")
            game = Game.create_from_preset(
                preset_name="single_model_test",
                model_config_manager=model_manager,
                enable_human_scoring=False,  # Set to True to enable human scoring
                human_scoring_port=5001
            )
        else:
            raise ValueError("No suitable preset found")
            
    except Exception as e:
        print(f"Preset creation failed: {e}")
        print("\nOption 2: Creating game with manual configuration...")
        
        # Fallback: Manual configuration with model validation
        player_configs = [
            {"name": "Hearts", "model": "openai/gpt-4o-mini"},
            {"name": "Spades", "model": "openai/gpt-4o-mini"},
            {"name": "Diamonds", "model": "openai/gpt-4o-mini"},
            {"name": "Clubs", "model": "openai/gpt-4o-mini"}
        ]

        judge_configs = [
            {"name": "Justice", "model": "openai/gpt-4o-mini"},
            {"name": "Wisdom", "model": "openai/gpt-4o-mini"},
            {"name": "Truth", "model": "openai/gpt-4o-mini"},
            {"name": "Honor", "model": "openai/gpt-4o-mini"}
        ]

        print("\nPlayer configurations:")
        for config in player_configs:
            print(f"  {config['name']} -> {config['model']}")
        
        print("\nJudge configurations:")
        for config in judge_configs:
            print(f"  {config['name']} -> {config['model']}")
        
        # Create game with model validation
        game = Game(
            player_configs=player_configs,
            judge_configs=judge_configs,
            model_config_manager=model_manager,
            enable_human_scoring=False,  # Set to True to enable human scoring
            human_scoring_port=5001
        )
    
    print("\n" + "=" * 60)
    print("Starting Multi-LLM Debate Game!")
    print("=" * 60)
    
    # Start the game
    game.start_game()
    
    print("\n" + "=" * 60)
    print("Game completed! Thank you for playing.")
    print("=" * 60)
