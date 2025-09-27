"""
Model Performance Analytics System

This module provides comprehensive analytics and reporting capabilities for multi-LLM
game performance, including win rates, decision patterns, human scores, and export functionality.
"""

import json
import csv
import os
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict
from game_record import GameRecord, ModelPerformanceRecord


@dataclass
class ModelComparisonReport:
    """Comprehensive model comparison report"""
    model_name: str
    total_games: int
    wins: int
    win_rate: float
    average_score: float
    total_decisions: int
    average_response_time: float
    challenge_success_rate: float
    defense_success_rate: float
    human_score_average: float
    human_score_count: int
    decision_patterns: Dict[str, int]
    performance_trends: List[Dict[str, Any]]


@dataclass
class GameSessionAnalytics:
    """Analytics for a single game session"""
    game_id: str
    winner: str
    total_rounds: int
    total_decisions: int
    game_duration: float
    model_assignments: Dict[str, str]
    final_scores: Dict[str, float]
    human_scoring_enabled: bool
    error_incidents: List[Dict[str, Any]]


class ModelPerformanceAnalytics:
    """
    Comprehensive analytics system for model performance tracking and reporting.
    
    This class provides:
    - Model comparison reports with win rates and decision patterns
    - Statistics display for performance metrics and human scores
    - Export functionality for performance data in multiple formats
    - Trend analysis and performance insights
    """
    
    def __init__(self, game_records_dir: str = "game_records", 
                 reports_dir: str = "performance_reports"):
        """
        Initialize the analytics system.
        
        Args:
            game_records_dir: Directory containing game record files
            reports_dir: Directory to save performance reports
        """
        self.game_records_dir = Path(game_records_dir)
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(exist_ok=True)
        
        # Cache for loaded game records
        self._game_records_cache: Dict[str, GameRecord] = {}
        self._analytics_cache: Dict[str, Any] = {}
    
    def load_game_records(self, game_ids: Optional[List[str]] = None) -> List[GameRecord]:
        """
        Load game records from files.
        
        Args:
            game_ids: Optional list of specific game IDs to load. If None, loads all.
            
        Returns:
            List[GameRecord]: List of loaded game records
        """
        game_records = []
        
        if not self.game_records_dir.exists():
            print(f"Game records directory '{self.game_records_dir}' not found")
            return game_records
        
        # Get all JSON files in the game records directory
        record_files = list(self.game_records_dir.glob("*.json"))
        
        if game_ids:
            # Filter to only requested game IDs
            record_files = [f for f in record_files if f.stem in game_ids]
        
        for record_file in record_files:
            try:
                with open(record_file, 'r', encoding='utf-8') as f:
                    record_data = json.load(f)
                
                # Create GameRecord object from loaded data
                game_record = self._create_game_record_from_data(record_data)
                game_records.append(game_record)
                
                # Cache the loaded record
                self._game_records_cache[game_record.game_id] = game_record
                
            except Exception as e:
                print(f"Error loading game record '{record_file}': {e}")
        
        print(f"Loaded {len(game_records)} game records")
        return game_records
    
    def _create_game_record_from_data(self, data: Dict[str, Any]) -> GameRecord:
        """Create a GameRecord object from loaded JSON data"""
        game_record = GameRecord()
        game_record.game_id = data.get("game_id", "unknown")
        game_record.player_names = data.get("player_names", [])
        game_record.winner = data.get("winner")
        game_record.player_model_assignments = data.get("player_model_assignments", {})
        game_record.judge_model_assignments = data.get("judge_model_assignments", {})
        
        # Reconstruct model performance records
        model_performance_data = data.get("model_performance", {})
        for key, perf_data in model_performance_data.items():
            game_record.model_performance[key] = ModelPerformanceRecord(
                model_name=perf_data["model_name"],
                player_name=perf_data["player_name"],
                decision_count=perf_data.get("decision_count", 0),
                successful_challenges=perf_data.get("successful_challenges", 0),
                failed_challenges=perf_data.get("failed_challenges", 0),
                successful_defenses=perf_data.get("successful_defenses", 0),
                failed_defenses=perf_data.get("failed_defenses", 0),
                total_response_time=perf_data.get("total_response_time", 0.0),
                human_scores=perf_data.get("human_scores", [])
            )
        
        return game_record
    
    def generate_model_comparison_report(self, game_records: Optional[List[GameRecord]] = None) -> Dict[str, ModelComparisonReport]:
        """
        Generate comprehensive model comparison reports.
        
        Args:
            game_records: Optional list of game records. If None, loads all available records.
            
        Returns:
            Dict[str, ModelComparisonReport]: Model comparison reports keyed by model name
        """
        if game_records is None:
            game_records = self.load_game_records()
        
        if not game_records:
            print("No game records available for analysis")
            return {}
        
        # Aggregate data by model
        model_data: Dict[str, Dict[str, Any]] = {}
        
        for game_record in game_records:
            # Process each model's performance in this game
            for perf_key, perf_record in game_record.model_performance.items():
                model_name = perf_record.model_name
                
                if model_name not in model_data:
                    model_data[model_name] = {
                        "total_games": 0,
                        "wins": 0,
                        "total_decisions": 0,
                        "total_response_time": 0.0,
                        "successful_challenges": 0,
                        "failed_challenges": 0,
                        "successful_defenses": 0,
                        "failed_defenses": 0,
                        "human_scores": [],
                        "decision_patterns": {},
                        "performance_trends": [],
                        "scores": []
                    }
                
                data = model_data[model_name]
                data["total_games"] += 1
                
                # Check if this model won the game
                if game_record.winner and perf_record.player_name == game_record.winner:
                    data["wins"] += 1
                
                # Aggregate performance metrics
                data["total_decisions"] += perf_record.decision_count
                data["total_response_time"] += perf_record.total_response_time
                data["successful_challenges"] += perf_record.successful_challenges
                data["failed_challenges"] += perf_record.failed_challenges
                data["successful_defenses"] += perf_record.successful_defenses
                data["failed_defenses"] += perf_record.failed_defenses
                
                # Collect human scores
                data["human_scores"].extend(perf_record.human_scores)
                
                # Track performance trends (simplified for now)
                data["performance_trends"].append({
                    "game_id": game_record.game_id,
                    "player_name": perf_record.player_name,
                    "decision_count": perf_record.decision_count,
                    "challenge_success_rate": perf_record.challenge_success_rate,
                    "defense_success_rate": perf_record.defense_success_rate
                })
        
        # Generate comparison reports
        comparison_reports = {}
        
        for model_name, data in model_data.items():
            # Calculate aggregated metrics
            win_rate = data["wins"] / data["total_games"] if data["total_games"] > 0 else 0.0
            avg_response_time = (data["total_response_time"] / data["total_decisions"] 
                               if data["total_decisions"] > 0 else 0.0)
            
            total_challenges = data["successful_challenges"] + data["failed_challenges"]
            challenge_success_rate = (data["successful_challenges"] / total_challenges 
                                    if total_challenges > 0 else 0.0)
            
            total_defenses = data["successful_defenses"] + data["failed_defenses"]
            defense_success_rate = (data["successful_defenses"] / total_defenses 
                                  if total_defenses > 0 else 0.0)
            
            # Calculate human score average
            human_score_values = []
            for score_dict in data["human_scores"]:
                if isinstance(score_dict, dict):
                    human_score_values.extend(score_dict.values())
            
            human_score_average = (sum(human_score_values) / len(human_score_values) 
                                 if human_score_values else 0.0)
            
            # Create comparison report
            comparison_reports[model_name] = ModelComparisonReport(
                model_name=model_name,
                total_games=data["total_games"],
                wins=data["wins"],
                win_rate=win_rate,
                average_score=0.0,  # Would need judge scores to calculate this
                total_decisions=data["total_decisions"],
                average_response_time=avg_response_time,
                challenge_success_rate=challenge_success_rate,
                defense_success_rate=defense_success_rate,
                human_score_average=human_score_average,
                human_score_count=len(human_score_values),
                decision_patterns=data["decision_patterns"],
                performance_trends=data["performance_trends"]
            )
        
        return comparison_reports
    
    def display_model_statistics(self, comparison_reports: Optional[Dict[str, ModelComparisonReport]] = None) -> None:
        """
        Display comprehensive model performance statistics.
        
        Args:
            comparison_reports: Optional pre-generated comparison reports
        """
        if comparison_reports is None:
            comparison_reports = self.generate_model_comparison_report()
        
        if not comparison_reports:
            print("No model performance data available")
            return
        
        print("\n" + "="*80)
        print("MODEL PERFORMANCE STATISTICS")
        print("="*80)
        
        # Sort models by win rate for better display
        sorted_models = sorted(comparison_reports.items(), 
                             key=lambda x: x[1].win_rate, reverse=True)
        
        for model_name, report in sorted_models:
            print(f"\n📊 {model_name}")
            print("-" * 60)
            print(f"Games Played: {report.total_games}")
            print(f"Wins: {report.wins} ({report.win_rate:.1%})")
            print(f"Total Decisions: {report.total_decisions}")
            print(f"Average Response Time: {report.average_response_time:.2f}s")
            print(f"Challenge Success Rate: {report.challenge_success_rate:.1%}")
            print(f"Defense Success Rate: {report.defense_success_rate:.1%}")
            
            if report.human_score_count > 0:
                print(f"Human Score Average: {report.human_score_average:.2f}/5 ({report.human_score_count} scores)")
            else:
                print("Human Score Average: No human scores available")
        
        # Display summary statistics
        print("\n" + "="*80)
        print("SUMMARY STATISTICS")
        print("="*80)
        
        total_games = sum(report.total_games for report in comparison_reports.values())
        total_decisions = sum(report.total_decisions for report in comparison_reports.values())
        avg_response_time = (sum(report.average_response_time * report.total_decisions 
                               for report in comparison_reports.values()) / total_decisions
                           if total_decisions > 0 else 0.0)
        
        print(f"Total Games Analyzed: {total_games}")
        print(f"Total Decisions Made: {total_decisions}")
        print(f"Overall Average Response Time: {avg_response_time:.2f}s")
        print(f"Models Analyzed: {len(comparison_reports)}")
        
        # Find best performing model
        if comparison_reports:
            best_model = max(comparison_reports.items(), key=lambda x: x[1].win_rate)
            print(f"Best Performing Model: {best_model[0]} ({best_model[1].win_rate:.1%} win rate)")
    
    def export_performance_data(self, format_type: str = "json", 
                              filename: Optional[str] = None,
                              comparison_reports: Optional[Dict[str, ModelComparisonReport]] = None) -> str:
        """
        Export performance data to various formats.
        
        Args:
            format_type: Export format ("json", "csv", "html")
            filename: Optional custom filename
            comparison_reports: Optional pre-generated comparison reports
            
        Returns:
            str: Path to the exported file
        """
        if comparison_reports is None:
            comparison_reports = self.generate_model_comparison_report()
        
        if not comparison_reports:
            raise ValueError("No performance data available for export")
        
        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"model_performance_report_{timestamp}"
        
        if format_type.lower() == "json":
            return self._export_json(comparison_reports, filename)
        elif format_type.lower() == "csv":
            return self._export_csv(comparison_reports, filename)
        elif format_type.lower() == "html":
            return self._export_html(comparison_reports, filename)
        else:
            raise ValueError(f"Unsupported export format: {format_type}")
    
    def _export_json(self, comparison_reports: Dict[str, ModelComparisonReport], filename: str) -> str:
        """Export performance data as JSON"""
        filepath = self.reports_dir / f"{filename}.json"
        
        # Convert dataclass objects to dictionaries
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "models": {name: asdict(report) for name, report in comparison_reports.items()}
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"Performance data exported to: {filepath}")
        return str(filepath)
    
    def _export_csv(self, comparison_reports: Dict[str, ModelComparisonReport], filename: str) -> str:
        """Export performance data as CSV"""
        filepath = self.reports_dir / f"{filename}.csv"
        
        # Define CSV headers
        headers = [
            "model_name", "total_games", "wins", "win_rate", "total_decisions",
            "average_response_time", "challenge_success_rate", "defense_success_rate",
            "human_score_average", "human_score_count"
        ]
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            
            for model_name, report in comparison_reports.items():
                writer.writerow([
                    report.model_name,
                    report.total_games,
                    report.wins,
                    f"{report.win_rate:.3f}",
                    report.total_decisions,
                    f"{report.average_response_time:.3f}",
                    f"{report.challenge_success_rate:.3f}",
                    f"{report.defense_success_rate:.3f}",
                    f"{report.human_score_average:.3f}",
                    report.human_score_count
                ])
        
        print(f"Performance data exported to: {filepath}")
        return str(filepath)
    
    def _export_html(self, comparison_reports: Dict[str, ModelComparisonReport], filename: str) -> str:
        """Export performance data as HTML report"""
        filepath = self.reports_dir / f"{filename}.html"
        
        # Sort models by win rate
        sorted_reports = sorted(comparison_reports.items(), 
                              key=lambda x: x[1].win_rate, reverse=True)
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Model Performance Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .model-section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
        .stats-table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
        .stats-table th, .stats-table td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        .stats-table th {{ background-color: #f2f2f2; }}
        .win-rate {{ font-weight: bold; color: #2e7d32; }}
        .summary {{ background-color: #e3f2fd; padding: 15px; border-radius: 5px; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Model Performance Report</h1>
        <p>Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        <p>Models analyzed: {len(comparison_reports)}</p>
    </div>
"""
        
        # Add individual model sections
        for model_name, report in sorted_reports:
            html_content += f"""
    <div class="model-section">
        <h2>📊 {model_name}</h2>
        <table class="stats-table">
            <tr><th>Metric</th><th>Value</th></tr>
            <tr><td>Games Played</td><td>{report.total_games}</td></tr>
            <tr><td>Wins</td><td>{report.wins}</td></tr>
            <tr><td>Win Rate</td><td class="win-rate">{report.win_rate:.1%}</td></tr>
            <tr><td>Total Decisions</td><td>{report.total_decisions}</td></tr>
            <tr><td>Average Response Time</td><td>{report.average_response_time:.2f}s</td></tr>
            <tr><td>Challenge Success Rate</td><td>{report.challenge_success_rate:.1%}</td></tr>
            <tr><td>Defense Success Rate</td><td>{report.defense_success_rate:.1%}</td></tr>
            <tr><td>Human Score Average</td><td>{report.human_score_average:.2f}/5 ({report.human_score_count} scores)</td></tr>
        </table>
    </div>
"""
        
        # Add summary section
        total_games = sum(report.total_games for report in comparison_reports.values())
        total_decisions = sum(report.total_decisions for report in comparison_reports.values())
        best_model = max(comparison_reports.items(), key=lambda x: x[1].win_rate)
        
        html_content += f"""
    <div class="summary">
        <h2>Summary Statistics</h2>
        <p><strong>Total Games Analyzed:</strong> {total_games}</p>
        <p><strong>Total Decisions Made:</strong> {total_decisions}</p>
        <p><strong>Best Performing Model:</strong> {best_model[0]} ({best_model[1].win_rate:.1%} win rate)</p>
    </div>
</body>
</html>
"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"Performance data exported to: {filepath}")
        return str(filepath)
    
    def analyze_decision_patterns(self, game_records: Optional[List[GameRecord]] = None) -> Dict[str, Dict[str, Any]]:
        """
        Analyze decision patterns for each model.
        
        Args:
            game_records: Optional list of game records
            
        Returns:
            Dict: Decision pattern analysis by model
        """
        if game_records is None:
            game_records = self.load_game_records()
        
        pattern_analysis = {}
        
        for game_record in game_records:
            for perf_key, perf_record in game_record.model_performance.items():
                model_name = perf_record.model_name
                
                if model_name not in pattern_analysis:
                    pattern_analysis[model_name] = {
                        "total_challenges_made": 0,
                        "total_challenges_received": 0,
                        "aggressive_plays": 0,
                        "conservative_plays": 0,
                        "bluffing_attempts": 0,
                        "decision_speed_distribution": []
                    }
                
                # Analyze this model's patterns
                analysis = pattern_analysis[model_name]
                analysis["total_challenges_made"] += (perf_record.successful_challenges + 
                                                    perf_record.failed_challenges)
                analysis["total_challenges_received"] += (perf_record.successful_defenses + 
                                                        perf_record.failed_defenses)
                
                # Add response time to distribution
                if perf_record.decision_count > 0:
                    avg_time = perf_record.average_response_time
                    analysis["decision_speed_distribution"].append(avg_time)
        
        # Calculate additional metrics
        for model_name, analysis in pattern_analysis.items():
            total_interactions = (analysis["total_challenges_made"] + 
                                analysis["total_challenges_received"])
            analysis["interaction_rate"] = total_interactions
            
            if analysis["decision_speed_distribution"]:
                speeds = analysis["decision_speed_distribution"]
                analysis["avg_decision_speed"] = sum(speeds) / len(speeds)
                analysis["decision_speed_variance"] = sum((x - analysis["avg_decision_speed"])**2 
                                                        for x in speeds) / len(speeds)
            else:
                analysis["avg_decision_speed"] = 0.0
                analysis["decision_speed_variance"] = 0.0
        
        return pattern_analysis
    
    def generate_performance_insights(self, comparison_reports: Optional[Dict[str, ModelComparisonReport]] = None) -> List[str]:
        """
        Generate insights and recommendations based on performance data.
        
        Args:
            comparison_reports: Optional pre-generated comparison reports
            
        Returns:
            List[str]: List of insights and recommendations
        """
        if comparison_reports is None:
            comparison_reports = self.generate_model_comparison_report()
        
        if not comparison_reports:
            return ["No performance data available for analysis"]
        
        insights = []
        
        # Find best and worst performers
        sorted_by_winrate = sorted(comparison_reports.items(), 
                                 key=lambda x: x[1].win_rate, reverse=True)
        
        if len(sorted_by_winrate) >= 2:
            best_model = sorted_by_winrate[0]
            worst_model = sorted_by_winrate[-1]
            
            insights.append(f"🏆 Best performer: {best_model[0]} with {best_model[1].win_rate:.1%} win rate")
            insights.append(f"📉 Needs improvement: {worst_model[0]} with {worst_model[1].win_rate:.1%} win rate")
        
        # Analyze response times
        fastest_model = min(comparison_reports.items(), 
                          key=lambda x: x[1].average_response_time)
        slowest_model = max(comparison_reports.items(), 
                          key=lambda x: x[1].average_response_time)
        
        insights.append(f"⚡ Fastest responses: {fastest_model[0]} ({fastest_model[1].average_response_time:.2f}s avg)")
        insights.append(f"🐌 Slowest responses: {slowest_model[0]} ({slowest_model[1].average_response_time:.2f}s avg)")
        
        # Analyze challenge patterns
        best_challenger = max(comparison_reports.items(), 
                            key=lambda x: x[1].challenge_success_rate)
        best_defender = max(comparison_reports.items(), 
                          key=lambda x: x[1].defense_success_rate)
        
        insights.append(f"🎯 Best challenger: {best_challenger[0]} ({best_challenger[1].challenge_success_rate:.1%} success rate)")
        insights.append(f"🛡️ Best defender: {best_defender[0]} ({best_defender[1].defense_success_rate:.1%} success rate)")
        
        # Human scoring insights
        models_with_human_scores = [(name, report) for name, report in comparison_reports.items() 
                                  if report.human_score_count > 0]
        
        if models_with_human_scores:
            best_human_rated = max(models_with_human_scores, 
                                 key=lambda x: x[1].human_score_average)
            insights.append(f"👥 Highest human-rated: {best_human_rated[0]} ({best_human_rated[1].human_score_average:.2f}/5 avg)")
        
        # Performance consistency insights
        win_rates = [report.win_rate for report in comparison_reports.values()]
        if len(win_rates) > 1:
            win_rate_variance = sum((x - sum(win_rates)/len(win_rates))**2 for x in win_rates) / len(win_rates)
            if win_rate_variance < 0.01:  # Low variance
                insights.append("📊 Performance is well-balanced across models")
            else:
                insights.append("📊 Significant performance differences detected between models")
        
        return insights


def create_sample_analytics_report():
    """Create a sample analytics report for demonstration"""
    analytics = ModelPerformanceAnalytics()
    
    print("Model Performance Analytics Demo")
    print("=" * 50)
    
    # Load and analyze game records
    game_records = analytics.load_game_records()
    
    if not game_records:
        print("No game records found. Please run some games first.")
        return
    
    # Generate comparison reports
    print("\nGenerating model comparison reports...")
    comparison_reports = analytics.generate_model_comparison_report(game_records)
    
    # Display statistics
    analytics.display_model_statistics(comparison_reports)
    
    # Analyze decision patterns
    print("\nAnalyzing decision patterns...")
    decision_patterns = analytics.analyze_decision_patterns(game_records)
    
    if decision_patterns:
        print("\nDECISION PATTERN ANALYSIS")
        print("=" * 50)
        for model_name, patterns in decision_patterns.items():
            print(f"\n{model_name}:")
            print(f"  Challenges made: {patterns['total_challenges_made']}")
            print(f"  Challenges received: {patterns['total_challenges_received']}")
            print(f"  Average decision speed: {patterns['avg_decision_speed']:.2f}s")
    
    # Generate insights
    print("\nGenerating performance insights...")
    insights = analytics.generate_performance_insights(comparison_reports)
    
    print("\nPERFORMANCE INSIGHTS")
    print("=" * 50)
    for insight in insights:
        print(f"• {insight}")
    
    # Export data
    print("\nExporting performance data...")
    try:
        json_file = analytics.export_performance_data("json")
        csv_file = analytics.export_performance_data("csv")
        html_file = analytics.export_performance_data("html")
        
        print(f"Reports exported:")
        print(f"  JSON: {json_file}")
        print(f"  CSV: {csv_file}")
        print(f"  HTML: {html_file}")
    except Exception as e:
        print(f"Export failed: {e}")


if __name__ == "__main__":
    create_sample_analytics_report()