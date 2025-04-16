import random
from typing import List, Optional, Dict
from player import Player
from game_record import GameRecord, PlayerInitialState
from judge_panel import JudgePanel

class Game:
    def __init__(self, player_configs: List[Dict[str, str]], judge_configs: List[Dict[str, str]]) -> None:
        """初始化游戏
        
        Args:
            player_configs: 包含玩家配置的列表，每个配置是一个字典，包含 name 和 model 字段
        """
        # 使用配置创建玩家对象
        self.players = [Player(config["name"], config["model"]) for config in player_configs]
        
        # 初始化每个玩家对其他玩家的看法
        for player in self.players:
            player.init_opinions(self.players)
        
        self.deck: List[str] = []
        self.target_card: Optional[str] = None
        self.current_player_idx: int = random.randint(0, len(self.players) - 1)
        self.last_shooter_name: Optional[str] = None
        self.game_over: bool = False

        # Initialize judge panel
        self.judge_panel = JudgePanel(judge_configs)
        
        # 创建游戏记录
        self.game_record: GameRecord = GameRecord()
        self.game_record.start_game([p.name for p in self.players])
        self.round_count = 0
        
        # Initialize player scores
        self.judge_panel.initialize_scores([p.name for p in self.players])

    def _create_deck(self) -> List[str]:
        """创建并洗牌牌组"""
        deck = ['Q'] * 6 + ['K'] * 6 + ['A'] * 6 + ['Joker'] * 2
        random.shuffle(deck)
        return deck

    def deal_cards(self) -> None:
        """发牌并清空旧手牌"""
        self.deck = self._create_deck()
        for player in self.players:
            if player.alive:
                player.hand.clear()
        # 每位玩家发 5 张牌
        for _ in range(5):
            for player in self.players:
                if player.alive and self.deck:
                    player.hand.append(self.deck.pop())
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
                bullet_position=player.bullet_position,
                current_gun_position=player.current_bullet_position,
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

    def perform_penalty(self, player: Player) -> None:
        """
        执行射击惩罚，并根据结果更新游戏状态和记录

        Args:
            player: 需要执行惩罚的玩家
        """
        print(f"Player {player.name} is shooting!")
        
        # 执行射击并获取存活状态
        still_alive = player.process_penalty()
        self.last_shooter_name = player.name

        # 记录射击结果
        self.game_record.record_shooting(
            shooter_name=player.name,
            bullet_hit=not still_alive  # 如果玩家死亡，说明子弹命中
        )

        if not still_alive:
            print(f"{player.name} has died!")
        
        # 检查胜利条件
        if not self.check_victory():
            self.reset_round(record_shooter=True)

    def reset_round(self, record_shooter: bool) -> None:
        """重置当前小局"""
        print("Round reset, starting a new round!")

        # Get round info for judges
        round_info = {
            "base_info": self.game_record.get_latest_round_info(),
            "action_info": self.game_record.get_latest_round_actions(None, include_latest=True),
            "result": self.game_record.get_latest_round_result(None)
        }

        # Let judges evaluate the round
        self.judge_panel.evaluate_round(round_info)
        
        # Reveal votes and update scores
        vote_results = self.judge_panel.reveal_votes()
        print("\nJudge Votes:")
        for judge_name, vote in vote_results["votes"].items():
            print(f"{judge_name} voted for {vote['voted_player']}: {vote['reasoning']}")
        
        print(self.judge_panel.get_score_summary())
        
        # 在发新牌之前进行反思，并获取存活玩家列表
        alive_players = self.handle_reflection()

        # 重新发牌
        self.deal_cards()
        self.choose_target_card()

        if record_shooter and self.last_shooter_name:
            shooter_idx = next((i for i, p in enumerate(self.players)
                                if p.name == self.last_shooter_name), None)
            if shooter_idx is not None and self.players[shooter_idx].alive:
                self.current_player_idx = shooter_idx
            else:
                print(f"{self.last_shooter_name} is dead, moving to next alive player with cards")
                self.current_player_idx = self.find_next_player_with_cards(shooter_idx or 0)
        else:
            self.last_shooter_name = None
            self.current_player_idx = self.players.index(random.choice(alive_players))

        self.start_round_record()
        print(f"New round starting with {self.players[self.current_player_idx].name}!")

    def check_victory(self) -> bool:
        """
        检查胜利条件（仅剩一名存活玩家时），并记录胜利者
        
        Returns:
            bool: 游戏是否结束
        """
        alive_players = [p for p in self.players if p.alive]
        if len(alive_players) == 1:
            winner = alive_players[0]
            print(f"\n{winner.name} has won!")
            # 记录胜利者并保存游戏记录
            self.game_record.finish_game(winner.name)
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
        challenging_player_behavior = self.game_record.get_latest_play_behavior()

        # 检查是否需要添加额外提示
        extra_hint = "Note: All other players have no cards left." if self.check_other_players_no_cards(next_player) else ""

        # 让下一位玩家决定是否质疑
        challenge_result, reasoning = next_player.decide_challenge(
            round_base_info,
            round_action_info,
            challenge_decision_info,
            challenging_player_behavior,
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
        
        if is_valid:
            print(f"System challenge failed! {current_player.name}'s cards follow the rules.")
            # 记录一个特殊的射击结果（无人射击）
            self.game_record.record_shooting(
                shooter_name="none",
                bullet_hit=False
            )
            self.reset_round(record_shooter=False)
        else:
            print(f"System challenge successful! {current_player.name}'s cards violate rules, executing shooting penalty.")
            self.perform_penalty(current_player)

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
            # 获取针对当前玩家的轮次结果
            round_result = self.game_record.get_latest_round_result(player.name)
            
            # 执行反思
            player.reflect(
                alive_players=alive_player_names,
                round_base_info=round_base_info,
                round_action_info=round_action_info,
                round_result=round_result
            )

        return alive_players

    def play_round(self) -> None:
        """执行一轮游戏逻辑"""
        current_player = self.players[self.current_player_idx]

         # 当其他所有存活玩家都没有手牌时，系统自动对当前玩家进行质疑
        if self.check_other_players_no_cards(current_player):
            self.handle_system_challenge(current_player)
            return

        print(f"\nIt's {current_player.name}'s turn to play, target card is {self.target_card}")
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
                self.perform_penalty(player_to_penalize)
                return
            else:
                print(f"{next_player.name} chose not to challenge, game continues.")
                
        # 切换至下一玩家
        self.current_player_idx = next_idx

    def start_game(self) -> None:
        """启动游戏主循环"""
        self.deal_cards()
        self.choose_target_card()
        self.start_round_record()
        while not self.game_over:
            self.play_round()

if __name__ == '__main__':
    # 配置玩家信息, 其中model为你通过API调用的模型名称
    player_configs = [
        {
            "name": "Hearts",
            "model": "openai/gpt-4o-mini"
        },
        {
            "name": "Spades",
            "model": "openai/gpt-4o-mini"
        },
        {
            "name": "Diamonds",
            "model": "openai/gpt-4o-mini"
        },
        {
            "name": "Clubs",
            "model": "openai/gpt-4o-mini"
        }
    ]

    # Configure judge LLMs
    judge_configs = [
        {
            "name": "Justice",
            "model": "openai/gpt-4o-mini"
        },
        {
            "name": "Wisdom",
            "model": "openai/gpt-4o-mini"
        },
        {
            "name": "Truth",
            "model": "openai/gpt-4o-mini"
        },
        {
            "name": "Honor",
            "model": "openai/gpt-4o-mini"
        }
    ]

    print("Game started!")
    print("\nPlayer configurations:")
    for config in player_configs:
        print(f"Player: {config['name']}, Using model: {config['model']}")
    
    print("\nJudge configurations:")
    for config in judge_configs:
        print(f"Judge: {config['name']}, Using model: {config['model']}")
    print("-" * 50 + "\n")

    # 创建游戏实例并开始游戏
    game = Game(player_configs, judge_configs)
    game.start_game()
