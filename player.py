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
        """初始化玩家
        
        Args:
            name: 玩家名称
            model_name: 使用的 LLM 模型名称
        """
        self.name = name
        self.hand = []
        self.alive = True
        # LLM 相关初始化
        self.llm_client = LLMClient()
        self.model_name = model_name

    def _read_file(self, filepath: str) -> str:
        """读取文件内容"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except Exception as e:
            print(f"Failed to read file {filepath}: {str(e)}")
            return ""

    def print_status(self) -> None:
        """打印玩家状态"""
        print(f"{self.name} - Cards: {', '.join(self.hand)}")
        
    def init_opinions(self, other_players: List["Player"]) -> None:
        """初始化对其他玩家的看法
        
        Args:
            other_players: 其他玩家列表
        """
        self.opinions = {
            player.name: "Don't know this player yet"
            for player in other_players
            if player.name != self.name
        }

    def choose_cards_to_play(self,
                        round_base_info: str,
                        round_action_info: str,
                        play_decision_info: str) -> Dict:
        """
        玩家选择出牌
        
        Args:
            round_base_info: 轮次基础信息
            round_action_info: 轮次操作信息
            play_decision_info: 出牌决策信息
            
        Returns:
            tuple: (结果字典，推理内容)
            - 结果字典包含 played_cards, behavior 和 play_reason
            - 推理内容为 LLM 的原始推理过程
        """
        # 读取规则和模板
        rules = self._read_file(RULE_BASE_PATH)
        template = self._read_file(PLAY_CARD_PROMPT_TEMPLATE_PATH)
        
        # 准备当前手牌信息
        current_cards = ", ".join(self.hand)
        
        # 填充模板 - Construct the complete prompt by combining:
        prompt = template.format(
            rules=rules,                     # Game rules for context
            self_name=self.name,             # Player's own name for self-awareness
            round_base_info=round_base_info, # Current round state (e.g., target card)
            round_action_info=round_action_info,  # Previous actions in this round
            play_decision_info=play_decision_info,# Additional context for decision
            current_cards=current_cards      # Player's available cards
        )
        
        # 尝试获取有效的 JSON 响应，最多重试五次 - Retry mechanism for handling API failures
        for attempt in range(5):
            # 每次都发送相同的原始 prompt - Create message for LLM API
            messages = [
                {"role": "user", "content": prompt}  # Single message with formatted prompt
            ]
            
            try:
                # Make API call to LLM
                content, reasoning_content = self.llm_client.chat(messages, model=self.model_name)
                
                # 尝试从内容中提取 JSON 部分 - Extract JSON from potentially multi-line response
                json_match = re.search(r'({[\s\S]*})', content)  # Regex matches JSON across lines
                if json_match:
                    json_str = json_match.group(1)  # Get the JSON string
                    result = json.loads(json_str)   # Parse JSON into dict
                    
                    # 验证 JSON 格式是否符合要求 - Validate response structure
                    if all(key in result for key in ["played_cards", "behavior", "talk", "play_reason"]):
                        # 确保 played_cards 是列表 - Convert single card to list if needed
                        if not isinstance(result["played_cards"], list):
                            result["played_cards"] = [result["played_cards"]]  # Wrap single card in list
                        
                        # 确保选出的牌是有效的（从手牌中选择 1-3 张）- Validate card selection
                        valid_cards = all(card in self.hand for card in result["played_cards"])  # All cards must be in hand
                        valid_count = 1 <= len(result["played_cards"]) <= 3  # Must play 1-3 cards
                        
                        if valid_cards and valid_count:
                            # 从手牌中移除已出的牌 - Remove played cards from hand
                            for card in result["played_cards"]:
                                self.hand.remove(card)  # Update player's hand
                            return result, reasoning_content  # Return decision and LLM reasoning
                                
            except Exception as e:
                # 仅记录错误，不修改重试请求
                print(f"Attempt {attempt+1} parsing failed: {str(e)}")
        raise RuntimeError(f"Player {self.name}'s choose_cards_to_play method failed after multiple attempts")

    def decide_challenge(self,
                        round_base_info: str,
                        round_action_info: str,
                        challenge_decision_info: str,
                        challenged_player_performance: str,
                        extra_hint: str) -> bool:
        """
        玩家决定是否对上一位玩家的出牌进行质疑
        
        Args:

            round_base_info: 轮次基础信息
            round_action_info: 轮次操作信息
            challenge_decision_info: 质疑决策信息
            challenged_player_performance: 被质疑玩家的表现描述
                The challenged_player_performance parameter originates from the get_latest_play_behavior() method in the RoundRecord class (game_record.py). It's a formatted string that describes the last player's action, including:
                    - Who played
                    - How many cards they claimed to play
                    - What the target card was
                    - How many cards they have remaining
                    - Their behavior during the play
                The flow is:
                    - Game.handle_challenge() gets this information by calling game_record.
                    - get_latest_play_behavior()
                    - This delegates to the current round's get_latest_play_behavior() method
                    - The method formats the last PlayAction record into a descriptive string
                    - This string is then passed to the next player's decide_challenge() method as challenged_player_performance

            extra_hint: 额外提示信息
            
        Returns:
            tuple: (result, reasoning_content)
            - result: 包含 was_challenged 和 challenge_reason 的字典
            - reasoning_content: LLM 的原始推理过程
        """
        # 读取规则和模板
        rules = self._read_file(RULE_BASE_PATH)
        template = self._read_file(CHALLENGE_PROMPT_TEMPLATE_PATH)
        self_hand = f"Your current cards are: {', '.join(self.hand)}"
        
        # 填充模板 - Format challenge decision prompt with:
        prompt = template.format(
            rules=rules,                     # Game rules context
            self_name=self.name,             # Player's own name
            round_base_info=round_base_info, # Current round state
            round_action_info=round_action_info,     # Actions taken this round
            self_hand=self_hand,                     # Player's current cards
            challenge_decision_info=challenge_decision_info,  # Challenge context
            challenged_player_performance=challenged_player_performance,  # Target's behavior
            extra_hint=extra_hint           # Any additional strategic hints
        )
        
        # 尝试获取有效的 JSON 响应，最多重试五次
        for attempt in range(5):
            # 每次都发送相同的原始 prompt
            messages = [
                {"role": "user", "content": prompt}
            ]
            
            try:
                # Make API call and get response
                content, reasoning_content = self.llm_client.chat(messages, model=self.model_name)
                
                # 解析 JSON 响应 - Extract JSON from LLM response
                json_match = re.search(r'({[\s\S]*})', content)  # Match JSON across lines
                if json_match:
                    json_str = json_match.group(1)  # Extract matched JSON
                    result = json.loads(json_str)   # Parse into dictionary
                    
                    # 验证 JSON 格式是否符合要求 - Validate response format
                    if all(key in result for key in ["was_challenged", "challenge_reason"]):
                        # 确保 was_challenged 是布尔值 - Ensure boolean challenge decision
                        if isinstance(result["was_challenged"], bool):
                            return result, reasoning_content  # Return decision and reasoning
                
            except Exception as e:
                # 仅记录错误，不修改重试请求
                print(f"Attempt {attempt+1} parsing failed: {str(e)}")
        raise RuntimeError(f"Player {self.name}'s decide_challenge method failed after multiple attempts")

    def reflect(self, alive_players: List[str], round_base_info: str, round_action_info: str) -> None:
        """
        玩家在轮次结束后对其他存活玩家进行反思，更新对他们的印象
        
        Args:
            alive_players: 还存活的玩家名称列表
            round_base_info: 轮次基础信息
            round_action_info: 轮次操作信息
        """
        # 读取反思模板
        template = self._read_file(REFLECT_PROMPT_TEMPLATE_PATH)  # Load reflection template
        
        # 读取规则 - Load game rules
        rules = self._read_file(RULE_BASE_PATH)  # Rules provide context for reflection
        
        # 对每个存活的玩家进行反思和印象更新（排除自己）- Update opinions of other players
        for player_name in alive_players:
            # 跳过对自己的反思 - Skip self reflection
            if player_name == self.name:
                continue
            
            # 获取此前对该玩家的印象 - Get previous impression
            previous_opinion = self.opinions.get(player_name, "Don't know this player yet")  # Default if no previous opinion
            
            # 填充模板 - Format reflection prompt with current context
            prompt = template.format(
                rules=rules,                     # Game rules for context
                self_name=self.name,             # Self identifier
                round_base_info=round_base_info, # Round state
                round_action_info=round_action_info,  # Actions this round
                player=player_name,              # Target player
                previous_opinion=previous_opinion # Previous analysis
            )
            
            # 向 LLM 请求分析 - Request player analysis from LLM
            messages = [
                {"role": "user", "content": prompt}  # Single message with reflection prompt
            ]
            
            try:
                # Get LLM's analysis
                content, _ = self.llm_client.chat(messages, model=self.model_name)
                
                # 更新对该玩家的印象 - Update stored opinion
                self.opinions[player_name] = content.strip()  # Clean response
                print(f"{self.name} updated opinion of {player_name}")  # Log update
                
            except Exception as e:
                # Log reflection errors but continue with other players
                print(f"Error while reflecting on player {player_name}: {str(e)}")
