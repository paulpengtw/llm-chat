#!/usr/bin/env python3
"""
Test script for the Human Scoring Interface

This script demonstrates and tests the HumanScoringInterface functionality
including session management, score collection, and web interface.
"""

import time
import threading
from human_scoring_interface import HumanScoringInterface

def test_basic_functionality():
    """Test basic functionality of the HumanScoringInterface"""
    print("Testing Human Scoring Interface...")
    
    # Initialize the interface
    interface = HumanScoringInterface(web_port=5001)
    
    # Test round information
    round_info = {
        "round_id": 1,
        "target_card": "K",
        "starting_player": "Alice",
        "round_players": ["Alice", "Bob", "Charlie", "Diana"]
    }
    
    players = ["Alice", "Bob", "Charlie", "Diana"]
    
    print(f"Starting scoring session for round {round_info['round_id']}")
    print(f"Players: {', '.join(players)}")
    print(f"Web interface available at: http://127.0.0.1:5001")
    
    # Start scoring session
    interface.start_scoring_session(round_info, players, timeout=300)
    
    print("\nScoring session started!")
    print("Open your web browser and navigate to http://127.0.0.1:5001")
    print("You can now score the players' performance.")
    print("\nWaiting for scores to be submitted...")
    print("(This will timeout after 5 minutes if no scores are submitted)")
    
    # Collect scores (this will block until scores are submitted or timeout)
    scores = interface.collect_scores(timeout=300)
    
    if scores:
        print("\n" + "="*50)
        print("SCORES COLLECTED!")
        print("="*50)
        for player, player_scores in scores.items():
            print(f"\n{player}:")
            for criterion, score in player_scores.items():
                criterion_display = criterion.replace('_', ' ').title()
                print(f"  {criterion_display}: {score}/5")
            
            # Calculate average
            avg_score = sum(player_scores.values()) / len(player_scores)
            print(f"  Average: {avg_score:.1f}/5")
    else:
        print("\nNo scores were collected (timeout or no submissions)")
    
    # Display statistics
    stats = interface.get_scoring_statistics()
    print(f"\nScoring Statistics:")
    print(f"  Total sessions: {stats['total_sessions']}")
    print(f"  Completed sessions: {stats['completed_sessions']}")
    print(f"  Timeout sessions: {stats['timeout_sessions']}")
    print(f"  Average scoring time: {stats['average_scoring_time']:.1f}s")
    
    # Test round summary display
    ai_votes = {
        "votes": {
            "Judge1": {"voted_player": "Alice", "reasoning": "Excellent strategic play"},
            "Judge2": {"voted_player": "Bob", "reasoning": "Great bluffing skills"},
            "Judge3": {"voted_player": "Alice", "reasoning": "Consistent performance"},
            "Judge4": {"voted_player": "Charlie", "reasoning": "Good reasoning"}
        }
    }
    
    interface.display_round_summary(round_info, ai_votes, scores)
    
    print("\nTest completed!")

def test_concurrent_sessions():
    """Test handling of multiple concurrent requests"""
    print("\nTesting concurrent session handling...")
    
    interface = HumanScoringInterface(web_port=5002)
    
    # Test starting multiple sessions (should replace previous)
    round1 = {"round_id": 1, "target_card": "K", "round_players": ["A", "B"]}
    round2 = {"round_id": 2, "target_card": "Q", "round_players": ["C", "D"]}
    
    interface.start_scoring_session(round1, ["A", "B"], timeout=60)
    time.sleep(1)
    interface.start_scoring_session(round2, ["C", "D"], timeout=60)
    
    print("Started two sessions - second should replace first")
    print("Interface available at: http://127.0.0.1:5002")
    
    # Quick timeout test
    scores = interface.collect_scores(timeout=5)
    print(f"Quick timeout test - scores collected: {len(scores)} players")

def test_validation():
    """Test score validation functionality"""
    print("\nTesting score validation...")
    
    interface = HumanScoringInterface(web_port=5003)
    
    # Test with invalid data
    round_info = {"round_id": 99, "target_card": "A", "round_players": ["TestPlayer"]}
    interface.start_scoring_session(round_info, ["TestPlayer"], timeout=30)
    
    print("Validation test session started at: http://127.0.0.1:5003")
    print("Try submitting invalid scores (outside 0-5 range) to test validation")
    
    # Short timeout for testing
    scores = interface.collect_scores(timeout=30)
    print(f"Validation test completed - scores: {scores}")

if __name__ == "__main__":
    print("Human Scoring Interface Test Suite")
    print("=" * 50)
    
    try:
        # Run basic functionality test
        test_basic_functionality()
        
        # Wait a moment between tests
        time.sleep(2)
        
        # Run concurrent sessions test
        test_concurrent_sessions()
        
        # Wait a moment between tests
        time.sleep(2)
        
        # Run validation test
        test_validation()
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\nAll tests completed!")