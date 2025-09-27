#!/usr/bin/env python3
"""
Command-line interface for Model Performance Analytics

This script provides a command-line interface for generating model performance
reports, analyzing decision patterns, and exporting data in various formats.
"""

import argparse
import sys
from pathlib import Path
from model_performance_analytics import ModelPerformanceAnalytics


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="Generate model performance reports and analytics",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --report                    # Generate and display performance report
  %(prog)s --export json               # Export performance data as JSON
  %(prog)s --export csv --output my_report  # Export as CSV with custom filename
  %(prog)s --patterns                  # Analyze decision patterns
  %(prog)s --insights                  # Generate performance insights
  %(prog)s --games game1 game2         # Analyze specific games only
        """
    )
    
    parser.add_argument(
        "--records-dir",
        default="game_records",
        help="Directory containing game record files (default: game_records)"
    )
    
    parser.add_argument(
        "--reports-dir", 
        default="performance_reports",
        help="Directory to save performance reports (default: performance_reports)"
    )
    
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate and display comprehensive performance report"
    )
    
    parser.add_argument(
        "--export",
        choices=["json", "csv", "html"],
        help="Export performance data in specified format"
    )
    
    parser.add_argument(
        "--output",
        help="Custom filename for exported report (without extension)"
    )
    
    parser.add_argument(
        "--patterns",
        action="store_true",
        help="Analyze and display decision patterns"
    )
    
    parser.add_argument(
        "--insights",
        action="store_true",
        help="Generate performance insights and recommendations"
    )
    
    parser.add_argument(
        "--games",
        nargs="+",
        help="Analyze specific game IDs only"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    # If no action specified, show help
    if not any([args.report, args.export, args.patterns, args.insights]):
        parser.print_help()
        return
    
    try:
        # Initialize analytics system
        analytics = ModelPerformanceAnalytics(
            game_records_dir=args.records_dir,
            reports_dir=args.reports_dir
        )
        
        if args.verbose:
            print(f"Loading game records from: {args.records_dir}")
        
        # Load game records
        game_records = analytics.load_game_records(args.games)
        
        if not game_records:
            print("❌ No game records found. Please run some games first.")
            return
        
        if args.verbose:
            print(f"Loaded {len(game_records)} game records")
        
        # Generate comparison reports (used by multiple actions)
        comparison_reports = None
        if args.report or args.export or args.insights:
            if args.verbose:
                print("Generating model comparison reports...")
            comparison_reports = analytics.generate_model_comparison_report(game_records)
        
        # Execute requested actions
        if args.report:
            print("📊 GENERATING PERFORMANCE REPORT")
            print("=" * 60)
            analytics.display_model_statistics(comparison_reports)
        
        if args.patterns:
            print("\n🎯 ANALYZING DECISION PATTERNS")
            print("=" * 60)
            decision_patterns = analytics.analyze_decision_patterns(game_records)
            
            if decision_patterns:
                for model_name, patterns in decision_patterns.items():
                    print(f"\n📈 {model_name}")
                    print("-" * 40)
                    print(f"Challenges made: {patterns['total_challenges_made']}")
                    print(f"Challenges received: {patterns['total_challenges_received']}")
                    print(f"Interaction rate: {patterns['interaction_rate']}")
                    print(f"Average decision speed: {patterns['avg_decision_speed']:.2f}s")
                    if patterns['decision_speed_variance'] > 0:
                        print(f"Decision speed variance: {patterns['decision_speed_variance']:.3f}")
            else:
                print("No decision pattern data available")
        
        if args.insights:
            print("\n💡 PERFORMANCE INSIGHTS")
            print("=" * 60)
            insights = analytics.generate_performance_insights(comparison_reports)
            
            for insight in insights:
                print(f"• {insight}")
        
        if args.export:
            print(f"\n📤 EXPORTING DATA AS {args.export.upper()}")
            print("=" * 60)
            
            try:
                filepath = analytics.export_performance_data(
                    format_type=args.export,
                    filename=args.output,
                    comparison_reports=comparison_reports
                )
                print(f"✅ Export successful: {filepath}")
                
            except Exception as e:
                print(f"❌ Export failed: {e}")
                sys.exit(1)
        
        print("\n✅ Analysis complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()