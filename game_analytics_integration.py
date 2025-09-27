"""
Game Analytics Integration

This module provides integration between the game system and the analytics system,
allowing for real-time performance tracking and post-game analysis.
"""

from typing import Dict, List, Optional, Any
from game_record import GameRecord
from model_performance_analytics import ModelPerformanceAnalytics, GameSessionAnalytics
from datetime import datetime


class GameAnalyticsManager:
    """
    Manages analytics integration for game sessions.
    
    This class provides:
    - Real-time performance tracking during games
    - Post-game analysis and reporting
    - Integration with existing game systems
    - Automatic report generation
    """
    
    def __init__(self, analytics: Optional[ModelPerformanceAnalytics] = None):
        """
        Initialize the analytics manager.
        
        Args:
            analytics: Optional pre-configured analytics instance
        """
        self.analytics = analytics or ModelPerformanceAnalytics()
        self.current_session: Optional[GameSessionAnalytics] = None
        self.session_start_time: Optional[datetime] = None
    
    def start_game_session(self, game_record: GameRecord) -> None:
        """
        Start tracking a new game session.
        
        Args:
            game_record: The game record to track
        """
        self.session_start_time = datetime.now()
        
        # Create session analytics object
        self.current_session = GameSessionAnalytics(
            game_id=game_record.game_id,
            winner="",  # Will be updated when game ends
            total_rounds=0,
            total_decisions=0,
            game_duration=0.0,
            model_assignments=game_record.player_model_assignments.copy(),
            final_scores={},
            human_scoring_enabled=False,  # Will be detected during game
            error_incidents=[]
        )
        
        print(f"📊 Started analytics tracking for game: {game_record.game_id}")
    
    def update_session_progress(self, game_record: GameRecord) -> None:
        """
        Update session progress with current game state.
        
        Args:
            game_record: Current game record
        """
        if not self.current_session:
            return
        
        # Update session metrics
        self.current_session.total_rounds = len(game_record.rounds)
        self.current_session.total_decisions = sum(
            perf.decision_count for perf in game_record.model_performance.values()
        )
        
        # Check for human scoring
        for perf_record in game_record.model_performance.values():
            if perf_record.human_scores:
                self.current_session.human_scoring_enabled = True
                break
    
    def record_error_incident(self, model_name: str, player_name: str, 
                            error_type: str, error_message: str) -> None:
        """
        Record an error incident during the game.
        
        Args:
            model_name: Name of the model that experienced the error
            player_name: Name of the player affected
            error_type: Type of error (e.g., "timeout", "api_failure", "validation_error")
            error_message: Detailed error message
        """
        if not self.current_session:
            return
        
        incident = {
            "timestamp": datetime.now().isoformat(),
            "model_name": model_name,
            "player_name": player_name,
            "error_type": error_type,
            "error_message": error_message
        }
        
        self.current_session.error_incidents.append(incident)
        print(f"⚠️  Recorded error incident: {model_name} - {error_type}")
    
    def end_game_session(self, game_record: GameRecord, final_scores: Optional[Dict[str, float]] = None) -> GameSessionAnalytics:
        """
        End the current game session and finalize analytics.
        
        Args:
            game_record: Final game record
            final_scores: Optional final scores from judge panel
            
        Returns:
            GameSessionAnalytics: Completed session analytics
        """
        if not self.current_session or not self.session_start_time:
            raise ValueError("No active game session to end")
        
        # Calculate game duration
        end_time = datetime.now()
        duration = (end_time - self.session_start_time).total_seconds()
        
        # Update final session data
        self.current_session.winner = game_record.winner or "Unknown"
        self.current_session.total_rounds = len(game_record.rounds)
        self.current_session.total_decisions = sum(
            perf.decision_count for perf in game_record.model_performance.values()
        )
        self.current_session.game_duration = duration
        self.current_session.final_scores = final_scores or {}
        
        # Final update for human scoring detection
        for perf_record in game_record.model_performance.values():
            if perf_record.human_scores:
                self.current_session.human_scoring_enabled = True
                break
        
        completed_session = self.current_session
        self.current_session = None
        self.session_start_time = None
        
        print(f"📊 Completed analytics tracking for game: {completed_session.game_id}")
        print(f"   Duration: {duration:.1f}s, Rounds: {completed_session.total_rounds}, "
              f"Decisions: {completed_session.total_decisions}")
        
        return completed_session
    
    def generate_post_game_report(self, game_record: GameRecord, 
                                display_report: bool = True,
                                export_formats: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Generate a comprehensive post-game report.
        
        Args:
            game_record: The completed game record
            display_report: Whether to display the report to console
            export_formats: Optional list of formats to export ("json", "csv", "html")
            
        Returns:
            Dict: Report data and export file paths
        """
        # Load this game's record for analysis
        game_records = [game_record]
        
        # Generate comparison reports
        comparison_reports = self.analytics.generate_model_comparison_report(game_records)
        
        # Analyze decision patterns
        decision_patterns = self.analytics.analyze_decision_patterns(game_records)
        
        # Generate insights
        insights = self.analytics.generate_performance_insights(comparison_reports)
        
        report_data = {
            "game_id": game_record.game_id,
            "comparison_reports": comparison_reports,
            "decision_patterns": decision_patterns,
            "insights": insights,
            "session_analytics": game_record.get_game_session_analytics(),
            "export_files": []
        }
        
        if display_report:
            self._display_post_game_report(report_data)
        
        # Export in requested formats
        if export_formats:
            for format_type in export_formats:
                try:
                    filename = f"post_game_report_{game_record.game_id}"
                    filepath = self.analytics.export_performance_data(
                        format_type=format_type,
                        filename=filename,
                        comparison_reports=comparison_reports
                    )
                    report_data["export_files"].append(filepath)
                except Exception as e:
                    print(f"Failed to export {format_type} report: {e}")
        
        return report_data
    
    def _display_post_game_report(self, report_data: Dict[str, Any]) -> None:
        """Display post-game report to console"""
        print("\n" + "="*80)
        print("POST-GAME PERFORMANCE REPORT")
        print("="*80)
        
        session_data = report_data["session_analytics"]
        print(f"Game ID: {session_data['game_id']}")
        print(f"Winner: {session_data['winner']}")
        print(f"Total Rounds: {session_data['total_rounds']}")
        print(f"Total Decisions: {session_data['total_decisions']}")
        
        # Display model performance
        print("\n📊 MODEL PERFORMANCE")
        print("-" * 50)
        self.analytics.display_model_statistics(report_data["comparison_reports"])
        
        # Display decision patterns
        decision_patterns = report_data["decision_patterns"]
        if decision_patterns:
            print("\n🎯 DECISION PATTERNS")
            print("-" * 50)
            for model_name, patterns in decision_patterns.items():
                print(f"{model_name}:")
                print(f"  Challenges made: {patterns['total_challenges_made']}")
                print(f"  Challenges received: {patterns['total_challenges_received']}")
                print(f"  Average decision speed: {patterns['avg_decision_speed']:.2f}s")
        
        # Display insights
        insights = report_data["insights"]
        if insights:
            print("\n💡 PERFORMANCE INSIGHTS")
            print("-" * 50)
            for insight in insights:
                print(f"• {insight}")
        
        # Display human scoring summary if available
        human_data = session_data.get("human_scoring_data", {})
        if human_data.get("total_human_scores", 0) > 0:
            print("\n👥 HUMAN SCORING SUMMARY")
            print("-" * 50)
            print(f"Total human scores: {human_data['total_human_scores']}")
            print("Average scores by model:")
            for model, avg_score in human_data.get("average_human_scores_by_model", {}).items():
                print(f"  {model}: {avg_score:.2f}/5")
        
        print("\n" + "="*80)
    
    def get_real_time_statistics(self, game_record: GameRecord) -> Dict[str, Any]:
        """
        Get real-time statistics for the current game.
        
        Args:
            game_record: Current game record
            
        Returns:
            Dict: Real-time statistics
        """
        stats = {
            "current_round": len(game_record.rounds),
            "total_decisions": sum(perf.decision_count for perf in game_record.model_performance.values()),
            "model_performance": {},
            "session_duration": 0.0
        }
        
        # Calculate session duration
        if self.session_start_time:
            duration = (datetime.now() - self.session_start_time).total_seconds()
            stats["session_duration"] = duration
        
        # Get current model performance
        for perf_key, perf_record in game_record.model_performance.items():
            stats["model_performance"][perf_record.model_name] = {
                "player_name": perf_record.player_name,
                "decisions": perf_record.decision_count,
                "avg_response_time": perf_record.average_response_time,
                "challenge_success_rate": perf_record.challenge_success_rate,
                "defense_success_rate": perf_record.defense_success_rate
            }
        
        return stats
    
    def compare_with_historical_data(self, current_game_record: GameRecord) -> Dict[str, Any]:
        """
        Compare current game performance with historical data.
        
        Args:
            current_game_record: Current game record to compare
            
        Returns:
            Dict: Comparison results
        """
        # Load all historical game records
        historical_records = self.analytics.load_game_records()
        
        # Filter out the current game if it's already saved
        historical_records = [record for record in historical_records 
                            if record.game_id != current_game_record.game_id]
        
        if not historical_records:
            return {"message": "No historical data available for comparison"}
        
        # Generate reports for historical and current data
        historical_reports = self.analytics.generate_model_comparison_report(historical_records)
        current_reports = self.analytics.generate_model_comparison_report([current_game_record])
        
        # Compare performance
        comparison_results = {
            "models_compared": [],
            "performance_changes": {},
            "historical_games": len(historical_records),
            "current_game": current_game_record.game_id
        }
        
        for model_name in current_reports.keys():
            if model_name in historical_reports:
                historical = historical_reports[model_name]
                current = current_reports[model_name]
                
                comparison_results["models_compared"].append(model_name)
                comparison_results["performance_changes"][model_name] = {
                    "win_rate_change": current.win_rate - historical.win_rate,
                    "response_time_change": current.average_response_time - historical.average_response_time,
                    "challenge_success_change": current.challenge_success_rate - historical.challenge_success_rate,
                    "historical_games": historical.total_games,
                    "historical_wins": historical.wins
                }
        
        return comparison_results


def create_analytics_integration_example():
    """Example of how to use the analytics integration"""
    from game_record import GameRecord
    
    print("Game Analytics Integration Example")
    print("=" * 50)
    
    # Create analytics manager
    manager = GameAnalyticsManager()
    
    # Simulate game session
    game_record = GameRecord()
    game_record.game_id = "example_game_001"
    game_record.player_names = ["Alice", "Bob", "Charlie", "Diana"]
    game_record.set_player_model_assignments({
        "Alice": "gpt-4o",
        "Bob": "gpt-4o-mini", 
        "Charlie": "claude-3-sonnet",
        "Diana": "claude-3-haiku"
    })
    
    # Start session tracking
    manager.start_game_session(game_record)
    
    # Simulate some game progress
    print("Simulating game progress...")
    manager.update_session_progress(game_record)
    
    # Simulate an error incident
    manager.record_error_incident(
        model_name="gpt-4o",
        player_name="Alice",
        error_type="timeout",
        error_message="Model response timeout after 30 seconds"
    )
    
    # Get real-time statistics
    real_time_stats = manager.get_real_time_statistics(game_record)
    print(f"Real-time stats: {real_time_stats}")
    
    # End session
    game_record.winner = "Alice"
    session_analytics = manager.end_game_session(game_record, {"Alice": 15, "Bob": 12, "Charlie": 10, "Diana": 8})
    
    print(f"Session completed: {session_analytics.game_id}")
    print(f"Winner: {session_analytics.winner}")
    print(f"Duration: {session_analytics.game_duration:.1f}s")


if __name__ == "__main__":
    create_analytics_integration_example()