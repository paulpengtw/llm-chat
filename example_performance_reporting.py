#!/usr/bin/env python3
"""
Example: Model Performance Reporting System

This script demonstrates the complete model performance reporting system including:
- Model performance analytics
- Web interface with real-time indicators
- Human scoring integration
- Export functionality
- Command-line reporting tools
"""

import sys
import time
import threading
from pathlib import Path

# Import our new modules
from model_performance_analytics import ModelPerformanceAnalytics, create_sample_analytics_report
from game_analytics_integration import GameAnalyticsManager
from web_human_scoring_integration import WebHumanScoringInterface
from terminal_stream.enhanced_main import main as run_enhanced_web_interface
from performance_report_cli import main as run_cli_report

def demonstrate_analytics_system():
    """Demonstrate the analytics system capabilities"""
    print("🔬 DEMONSTRATING MODEL PERFORMANCE ANALYTICS SYSTEM")
    print("=" * 70)
    
    print("\n1. 📊 Model Performance Analytics")
    print("-" * 40)
    
    # Create analytics instance
    analytics = ModelPerformanceAnalytics()
    
    # Load existing game records if any
    game_records = analytics.load_game_records()
    
    if game_records:
        print(f"Found {len(game_records)} existing game records")
        
        # Generate comparison reports
        comparison_reports = analytics.generate_model_comparison_report(game_records)
        
        # Display statistics
        analytics.display_model_statistics(comparison_reports)
        
        # Analyze decision patterns
        decision_patterns = analytics.analyze_decision_patterns(game_records)
        if decision_patterns:
            print("\n🎯 DECISION PATTERNS")
            print("-" * 30)
            for model_name, patterns in decision_patterns.items():
                print(f"{model_name}: {patterns['total_challenges_made']} challenges made, "
                      f"{patterns['avg_decision_speed']:.2f}s avg speed")
        
        # Generate insights
        insights = analytics.generate_performance_insights(comparison_reports)
        print("\n💡 PERFORMANCE INSIGHTS")
        print("-" * 30)
        for insight in insights:
            print(f"• {insight}")
        
        # Export data
        print("\n📤 EXPORTING DATA")
        print("-" * 30)
        try:
            json_file = analytics.export_performance_data("json", "demo_export")
            print(f"✅ JSON export: {json_file}")
            
            csv_file = analytics.export_performance_data("csv", "demo_export")
            print(f"✅ CSV export: {csv_file}")
            
            html_file = analytics.export_performance_data("html", "demo_export")
            print(f"✅ HTML export: {html_file}")
            
        except Exception as e:
            print(f"❌ Export failed: {e}")
    else:
        print("No existing game records found. Run some games first to see analytics.")

def demonstrate_web_interface():
    """Demonstrate the enhanced web interface"""
    print("\n2. 🌐 Enhanced Web Interface")
    print("-" * 40)
    
    print("The enhanced web interface includes:")
    print("• Real-time model performance indicators")
    print("• Live analytics dashboard")
    print("• Model information display")
    print("• Human scoring integration")
    print("• Enhanced game output with highlighting")
    print()
    print("To start the enhanced web interface:")
    print("  python terminal_stream/enhanced_main.py")
    print("  Then open: http://127.0.0.1:5000")
    print()

def demonstrate_human_scoring():
    """Demonstrate the web human scoring interface"""
    print("\n3. 👥 Web Human Scoring Interface")
    print("-" * 40)
    
    print("The web human scoring interface provides:")
    print("• Browser-based scoring forms")
    print("• Real-time score collection")
    print("• Multi-criteria evaluation")
    print("• Timeout handling")
    print("• Integration with main game interface")
    print()
    print("To test the human scoring interface:")
    print("  python web_human_scoring_integration.py")
    print("  Then open: http://127.0.0.1:5001")
    print()

def demonstrate_cli_tools():
    """Demonstrate the command-line tools"""
    print("\n4. 🖥️  Command-Line Analytics Tools")
    print("-" * 40)
    
    print("Available CLI commands:")
    print("• python performance_report_cli.py --report")
    print("• python performance_report_cli.py --export json")
    print("• python performance_report_cli.py --patterns")
    print("• python performance_report_cli.py --insights")
    print("• python performance_report_cli.py --games game1 game2")
    print()
    
    print("Example usage:")
    print("  # Generate comprehensive report")
    print("  python performance_report_cli.py --report --verbose")
    print()
    print("  # Export data and analyze patterns")
    print("  python performance_report_cli.py --export html --patterns --insights")
    print()

def demonstrate_integration():
    """Demonstrate the analytics integration with games"""
    print("\n5. 🔗 Analytics Integration")
    print("-" * 40)
    
    print("The analytics system integrates with games to provide:")
    print("• Real-time performance tracking")
    print("• Automatic report generation")
    print("• Error incident recording")
    print("• Historical data comparison")
    print("• Post-game analysis")
    print()
    
    # Example of analytics manager usage
    print("Example integration code:")
    print("""
    from game_analytics_integration import GameAnalyticsManager
    
    # Create analytics manager
    manager = GameAnalyticsManager()
    
    # Start tracking a game
    manager.start_game_session(game_record)
    
    # Update progress during game
    manager.update_session_progress(game_record)
    
    # Record errors if they occur
    manager.record_error_incident(
        model_name="gpt-4o",
        player_name="Alice", 
        error_type="timeout",
        error_message="Model response timeout"
    )
    
    # End session and generate report
    session_analytics = manager.end_game_session(game_record, final_scores)
    report = manager.generate_post_game_report(game_record, display_report=True)
    """)

def run_interactive_demo():
    """Run an interactive demonstration"""
    print("\n🎮 INTERACTIVE DEMO")
    print("=" * 50)
    
    print("Choose a demonstration:")
    print("1. Analytics System (analyze existing game records)")
    print("2. Enhanced Web Interface (start web server)")
    print("3. Human Scoring Interface (start scoring server)")
    print("4. CLI Tools (show command examples)")
    print("5. Run All Demonstrations")
    print("0. Exit")
    
    try:
        choice = input("\nEnter your choice (0-5): ").strip()
        
        if choice == "1":
            demonstrate_analytics_system()
        elif choice == "2":
            print("\nStarting enhanced web interface...")
            print("Press Ctrl+C to stop the server")
            run_enhanced_web_interface()
        elif choice == "3":
            print("\nStarting human scoring interface demo...")
            from web_human_scoring_integration import create_web_human_scoring_demo
            create_web_human_scoring_demo()
        elif choice == "4":
            demonstrate_cli_tools()
        elif choice == "5":
            demonstrate_analytics_system()
            demonstrate_web_interface()
            demonstrate_human_scoring()
            demonstrate_cli_tools()
            demonstrate_integration()
        elif choice == "0":
            print("Goodbye!")
            return
        else:
            print("Invalid choice. Please try again.")
            run_interactive_demo()
            
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\nDemo error: {e}")

def main():
    """Main function"""
    print("🚀 MODEL PERFORMANCE REPORTING SYSTEM DEMO")
    print("=" * 70)
    print()
    print("This demo showcases the complete model performance reporting system")
    print("implemented for the multi-LLM debate game, including:")
    print()
    print("✅ Model Performance Analytics")
    print("   - Comprehensive performance reports")
    print("   - Win rates, decision patterns, and human scores")
    print("   - Export functionality (JSON, CSV, HTML)")
    print()
    print("✅ Enhanced Web Interface")
    print("   - Real-time model performance indicators")
    print("   - Live analytics dashboard")
    print("   - Model information display")
    print("   - Enhanced game output with highlighting")
    print()
    print("✅ Human Scoring Integration")
    print("   - Web-based scoring interface")
    print("   - Real-time score collection")
    print("   - Multi-criteria evaluation")
    print()
    print("✅ Command-Line Tools")
    print("   - Flexible reporting options")
    print("   - Batch analysis capabilities")
    print("   - Export and visualization tools")
    print()
    
    if len(sys.argv) > 1:
        # Handle command-line arguments
        if sys.argv[1] == "--analytics":
            demonstrate_analytics_system()
        elif sys.argv[1] == "--web":
            print("Starting enhanced web interface...")
            run_enhanced_web_interface()
        elif sys.argv[1] == "--scoring":
            from web_human_scoring_integration import create_web_human_scoring_demo
            create_web_human_scoring_demo()
        elif sys.argv[1] == "--cli":
            demonstrate_cli_tools()
        elif sys.argv[1] == "--help":
            print("Usage:")
            print("  python example_performance_reporting.py [--analytics|--web|--scoring|--cli|--help]")
            print()
            print("Options:")
            print("  --analytics  Run analytics demonstration")
            print("  --web        Start enhanced web interface")
            print("  --scoring    Start human scoring interface demo")
            print("  --cli        Show CLI tools demonstration")
            print("  --help       Show this help message")
        else:
            print(f"Unknown option: {sys.argv[1]}")
            print("Use --help for available options")
    else:
        # Interactive mode
        run_interactive_demo()

if __name__ == "__main__":
    main()