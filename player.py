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
        self.bullet_position = random.randint(0, 5)
        self.current_bullet_position = 0
        self.opinions = {}
        
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
        print(f"{self.name} - Cards: {', '.join(self.hand)} - "
              f"Bullet Position: {self.bullet_position} - Current Chamber: {self.current_bullet_position}")
        
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
        
        # 填充模板
        prompt = template.format(
            rules=rules,
            self_name=self.name,
            round_base_info=round_base_info,
            round_action_info=round_action_info,
            play_decision_info=play_decision_info,
            current_cards=current_cards
        )
        
        # 尝试获取有效的 JSON 响应，最多重试五次
        for attempt in range(5):
            # 每次都发送相同的原始 prompt
            messages = [
                {"role": "user", "content": prompt}
            ]
            
            try:
                content, reasoning_content = self.llm_client.chat(messages, model=self.model_name)
                
                # 尝试从内容中提取 JSON 部分
                json_match = re.search(r'({[\s\S]*})', content)
                if json_match:
                    json_str = json_match.group(1)
                    result = json.loads(json_str)
                    
                    # 验证 JSON 格式是否符合要求
                    if all(key in result for key in ["played_cards", "behavior", "play_reason"]):
                        # 确保 played_cards 是列表
                        if not isinstance(result["played_cards"], list):
                            result["played_cards"] = [result["played_cards"]]
                        
                        # 确保选出的牌是有效的（从手牌中选择 1-3 张）
                        valid_cards = all(card in self.hand for card in result["played_cards"])
                        valid_count = 1 <= len(result["played_cards"]) <= 3
                        
                        if valid_cards and valid_count:
                            # 从手牌中移除已出的牌
                            for card in result["played_cards"]:
                                self.hand.remove(card)
                            return result, reasoning_content
                                
            except Exception as e:
                # 仅记录错误，不修改重试请求
                print(f"Attempt {attempt+1} parsing failed: {str(e)}")
        raise RuntimeError(f"Player {self.name}'s choose_cards_to_play method failed after multiple attempts")

    def decide_challenge(self,
                        round_base_info: str,
                        round_action_info: str,
                        challenge_decision_info: str,
                        challenging_player_performance: str,
                        extra_hint: str) -> bool:
        """
        玩家决定是否对上一位玩家的出牌进行质疑
        
        Args:

            round_base_info: 轮次基础信息
            round_action_info: 轮次操作信息
            challenge_decision_info: 质疑决策信息
            challenging_player_performance: 被质疑玩家的表现描述
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
        
        # 填充模板
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
        
        # 尝试获取有效的 JSON 响应，最多重试五次
        for attempt in range(5):
            # 每次都发送相同的原始 prompt
            messages = [
                {"role": "user", "content": prompt}
            ]
            
            try:
                content, reasoning_content = self.llm_client.chat(messages, model=self.model_name)
                
                # 解析 JSON 响应
                json_match = re.search(r'({[\s\S]*})', content)
                if json_match:
                    json_str = json_match.group(1)
                    result = json.loads(json_str)
                    
                    # 验证 JSON 格式是否符合要求
                    if all(key in result for key in ["was_challenged", "challenge_reason"]):
                        # 确保 was_challenged 是布尔值
                        if isinstance(result["was_challenged"], bool):
                            return result, reasoning_content
                
            except Exception as e:
                # 仅记录错误，不修改重试请求
                print(f"Attempt {attempt+1} parsing failed: {str(e)}")
        raise RuntimeError(f"Player {self.name}'s decide_challenge method failed after multiple attempts")

    def reflect(self, alive_players: List[str], round_base_info: str, round_action_info: str, round_result: str) -> None:
        """
        玩家在轮次结束后对其他存活玩家进行反思，更新对他们的印象
        
        Args:
            alive_players: 还存活的玩家名称列表
            round_base_info: 轮次基础信息
            round_action_info: 轮次操作信息
            round_result: 轮次结果
        """
        # 读取反思模板
        template = self._read_file(REFLECT_PROMPT_TEMPLATE_PATH)
        
        # 读取规则
        rules = self._read_file(RULE_BASE_PATH)
        
        # 对每个存活的玩家进行反思和印象更新（排除自己）
        for player_name in alive_players:
            # 跳过对自己的反思
            if player_name == self.name:
                continue
            
            # 获取此前对该玩家的印象
            previous_opinion = self.opinions.get(player_name, "Don't know this player yet")
            
            # 填充模板
            prompt = template.format(
                rules=rules,
                self_name=self.name,
                round_base_info=round_base_info,
                round_action_info=round_action_info,
                round_result=round_result,
                player=player_name,
                previous_opinion=previous_opinion
            )
            
            # 向 LLM 请求分析
            messages = [
                {"role": "user", "content": prompt}
            ]
            
            try:
                content, _ = self.llm_client.chat(messages, model=self.model_name)
                
                # 更新对该玩家的印象
                self.opinions[player_name] = content.strip()
                print(f"{self.name} updated opinion of {player_name}")
                
            except Exception as e:
                print(f"Error while reflecting on player {player_name}: {str(e)}")

    def process_penalty(self) -> bool:
        """处理惩罚"""
        print(f"Player {self.name} executing shooting penalty:")
        self.print_status()
        if self.bullet_position == self.current_bullet_position:
            print(f"{self.name} was shot and died!")
            self.alive = False
        else:
            print(f"{self.name} survived!")
        self.current_bullet_position = (self.current_bullet_position + 1) % 6
        return self.alive
