import random
from typing import List, Optional, Dict
from player import Player
from game_record import GameRecord, PlayerInitialState

class Game:
    def __init__(self, player_configs: List[Dict[str, str]]) -> None:
        """Initialize the debate game
        
        Args:
            player_configs: List of player configs, each containing name and model fields
        """
        # Create player objects from configs
        self.players = [Player(config["name"], config["model"]) for config in player_configs]
        
        # Initialize opinions between players
        for player in self.players:
            player.init_opinions(self.players)
        
        self.stance_cards = []
        self.current_topic: Optional[str] = None
        self.current_player_idx: int = random.randint(0, len(self.players) - 1)
        self.game_over: bool = False

        # Create game record
        self.game_record: GameRecord = GameRecord()
        self.game_record.start_game([p.name for p in self.players])
        self.round_count = 0

    def _create_stance_deck(self) -> List[str]:
        """Create and shuffle stance cards"""
        stances = ['Support', 'Oppose', 'Neutral'] * 6  
        random.shuffle(stances)
        return stances

    def deal_cards(self) -> None:
        """Deal new stance cards"""
        self.stance_cards = self._create_stance_deck()
        for player in self.players:
            player.hand.clear()
            
        # Deal 5 cards to each player
        for _ in range(5):
            for player in self.players:
                if self.stance_cards:
                    player.hand.append(self.stance_cards.pop())
                    player.print_status()

    def choose_debate_topic(self) -> None:
        """Choose a random debate topic"""
        topics = [
            "AI Ethics in Healthcare",
            "Climate Change Solutions",
            "Future of Education",
            "Space Exploration Benefits",
            "Digital Privacy Rights",
            "Renewable Energy Adoption",
            "Urban Development",
            "Technology in Education",
            "Remote Work Culture",
            "Sustainable Transportation"
        ]
        self.current_topic = random.choice(topics)
        print(f"Debate Topic: {self.current_topic}")

    def start_round_record(self) -> None:
        """Start a new round and record information in GameRecord"""
        self.round_count += 1
        starting_player = self.players[self.current_player_idx].name
        
        player_initial_states = [
            PlayerInitialState(
                player_name=player.name,
                bullet_position=0,  # Not used in debate format
                current_gun_position=0,  # Not used in debate format
                initial_hand=player.hand.copy()
            ) 
            for player in self.players
        ]

        # Get current players
        round_players = [player.name for player in self.players]

        # Create a deep copy of opinions
        player_opinions = {}
        for player in self.players:
            player_opinions[player.name] = {}
            for target, opinion in player.opinions.items():
                player_opinions[player.name][target] = opinion

        self.game_record.start_round(
            round_id=self.round_count,
            target_card=self.current_topic,
            round_players=round_players,
            starting_player=starting_player,
            player_initial_states=player_initial_states,
            player_opinions=player_opinions
        )

    def is_valid_argument(self, stances: List[str]) -> bool:
        """Check if argument stances are valid"""
        return len(stances) <= 3 and all(stance in ['Support', 'Oppose', 'Neutral'] for stance in stances)

    def find_next_player(self, start_idx: int) -> int:
        """Find index of next player with cards"""
        idx = start_idx
        for _ in range(len(self.players)):
            idx = (idx + 1) % len(self.players)
            if self.players[idx].hand:
                return idx
        return start_idx

    def handle_play_cards(self, current_player: Player, next_player: Player) -> List[str]:
        """Handle player's argument presentation
        
        Args:
            current_player: Current player
            next_player: Next player
            
        Returns:
            List[str]: Played stance cards
        """
        round_base_info = self.game_record.get_latest_round_info()
        round_action_info = self.game_record.get_latest_round_actions(current_player.name, include_latest=True)
        
        play_decision_info = self.game_record.get_play_decision_info(
            current_player.name,
            next_player.name
        )

        # Let current player choose cards
        play_result, reasoning = current_player.choose_cards_to_play(
            round_base_info,
            round_action_info,
            play_decision_info
        )

        # Record play action
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
    
    def handle_challenge(self, current_player: Player, next_player: Player, played_cards: List[str]) -> bool:
        """Handle argument challenge phase
        
        Args:
            current_player: Current player (being challenged)
            next_player: Next player (challenger)
            played_cards: Played stance cards
            
        Returns:
            bool: Whether challenge happened
        """
        round_base_info = self.game_record.get_latest_round_info()
        round_action_info = self.game_record.get_latest_round_actions(next_player.name, include_latest=False)
        
        challenge_decision_info = self.game_record.get_challenge_decision_info(
            next_player.name,
            current_player.name
        )

        challenging_player_behavior = self.game_record.get_latest_play_behavior()

        # Let next player decide whether to challenge
        challenge_result, reasoning = next_player.decide_challenge(
            round_base_info,
            round_action_info,
            challenge_decision_info,
            challenging_player_behavior,
            ""
        )

        if challenge_result["was_challenged"]:
            # Validate played cards
            is_valid = self.is_valid_argument(played_cards)
            
            # Record challenge
            self.game_record.record_challenge(
                was_challenged=True,
                reason=challenge_result["challenge_reason"],
                result=not is_valid,
                challenge_thinking=reasoning
            )
            
            return True
        else:
            # Record no challenge
            self.game_record.record_challenge(
                was_challenged=False,
                reason=challenge_result["challenge_reason"],
                result=None,
                challenge_thinking=reasoning
            )
            return False

    def reset_round(self) -> None:
        """Reset current round"""
        print("Starting new debate round!")

        # Handle reflection before new cards
        self.handle_reflection()

        # Deal new cards and choose topic
        self.deal_cards()
        self.choose_debate_topic()

        # Select random starting player
        self.current_player_idx = random.randint(0, len(self.players) - 1)

        self.start_round_record()
        print(f"{self.players[self.current_player_idx].name} starts this round!")

    def check_game_end(self) -> bool:
        """Check if game should end (after 10 rounds)
        
        Returns:
            bool: Whether game is over
        """
        if self.round_count >= 10:
            print("\nDebate concluded after 10 rounds!")
            self.game_record.finish_game("No winner - debate concluded")
            self.game_over = True
            return True
        return False
    
    def handle_reflection(self) -> None:
        """Handle player reflections"""
        alive_players = [p.name for p in self.players]
        
        # Get latest round information
        round_base_info = self.game_record.get_latest_round_info()
        
        # Let each player reflect
        for player in self.players:
            round_action_info = self.game_record.get_latest_round_actions(player.name, include_latest=True)
            round_result = self.game_record.get_latest_round_result(player.name)
            
            player.reflect(
                alive_players=alive_players,
                round_base_info=round_base_info,
                round_action_info=round_action_info,
                round_result=round_result
            )

    def play_round(self) -> None:
        """Execute one round of debate"""
        current_player = self.players[self.current_player_idx]

        print(f"\n{current_player.name}'s turn to present arguments on: {self.current_topic}")
        current_player.print_status()

        # Find next player with cards
        next_idx = self.find_next_player(self.current_player_idx)
        next_player = self.players[next_idx]

        # Handle argument presentation
        played_cards = self.handle_play_cards(current_player, next_player)

        # Handle potential challenge
        if next_player != current_player:
            challenged = self.handle_challenge(current_player, next_player, played_cards)
            if challenged:
                print("Starting new round after challenge!")
                self.reset_round()
                return
            else:
                print(f"{next_player.name} accepts the argument, debate continues.")
                
        # Switch to next player
        self.current_player_idx = next_idx

    def start_game(self) -> None:
        """Start main game loop"""
        self.deal_cards()
        self.choose_debate_topic()
        self.start_round_record()
        while not self.game_over:
            self.play_round()
            if self.check_game_end():
                break

if __name__ == '__main__':
    # Configure players
    player_configs = [
        {
            "name": "r",
            "model": "r1-1776"
        },
        {
            "name": "g",
            "model": "o3-mini"
        }
    ]

    print("Starting debate simulation between language models:")
    for config in player_configs:
        print(f"Model: {config['name']}, Using: {config['model']}")
    print("-" * 50)

    # Create and start game
    game = Game(player_configs)
    game.start_game()
