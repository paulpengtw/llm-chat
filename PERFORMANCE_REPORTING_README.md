# Model Performance Reporting System

This document describes the comprehensive model performance reporting system implemented for the multi-LLM debate game. The system provides detailed analytics, real-time monitoring, and export capabilities for analyzing LLM model performance.

## 🚀 Features

### 📊 Model Performance Analytics

- **Comprehensive Reports**: Win rates, decision patterns, response times, and human scores
- **Model Comparison**: Side-by-side performance analysis across different models
- **Decision Pattern Analysis**: Challenge behavior, response speed, and strategic patterns
- **Performance Insights**: Automated insights and recommendations
- **Export Functionality**: JSON, CSV, and HTML report formats

### 🌐 Enhanced Web Interface

- **Real-time Performance Indicators**: Live model performance metrics during games
- **Interactive Dashboard**: Visual analytics with model information display
- **Enhanced Game Output**: Syntax highlighting for model names and actions
- **Responsive Design**: Works on desktop and mobile devices
- **Auto-refresh**: Real-time updates without page reload

### 👥 Human Scoring Integration

- **Web-based Scoring**: Browser interface for human judges
- **Multi-criteria Evaluation**: Strategic thinking, bluffing, reasoning, overall performance
- **Real-time Collection**: Immediate score submission and aggregation
- **Timeout Handling**: Automatic session management with timeouts
- **Multi-judge Support**: Aggregate scores from multiple human evaluators

### 🖥️ Command-Line Tools

- **Flexible Reporting**: Generate reports for specific games or all historical data
- **Batch Analysis**: Process multiple game records efficiently
- **Export Options**: Multiple output formats with custom filenames
- **Verbose Mode**: Detailed logging and error reporting

## 📁 File Structure

```
├── model_performance_analytics.py      # Core analytics engine
├── game_analytics_integration.py       # Game integration layer
├── performance_report_cli.py           # Command-line interface
├── web_human_scoring_integration.py    # Web-based human scoring
├── example_performance_reporting.py    # Demonstration script
├── terminal_stream/
│   ├── enhanced_main.py               # Enhanced web interface
│   ├── enhanced_game_runner.py        # Web-integrated game runner
│   └── game_runner.py                 # Simple game runner
└── performance_reports/               # Generated reports directory
```

## 🛠️ Installation and Setup

### Prerequisites

- Python 3.8+
- Flask (for web interfaces)
- All existing game dependencies

### Setup

1. Ensure all game components are properly installed
2. The system automatically creates necessary directories
3. No additional installation required - uses existing dependencies

## 📖 Usage Guide

### 1. Analytics System

#### Basic Usage

```python
from model_performance_analytics import ModelPerformanceAnalytics

# Create analytics instance
analytics = ModelPerformanceAnalytics()

# Load and analyze game records
game_records = analytics.load_game_records()
comparison_reports = analytics.generate_model_comparison_report(game_records)

# Display statistics
analytics.display_model_statistics(comparison_reports)

# Export data
analytics.export_performance_data("html", "my_report")
```

#### Advanced Analysis

```python
# Analyze specific games
specific_games = analytics.load_game_records(["game_001", "game_002"])

# Decision pattern analysis
patterns = analytics.analyze_decision_patterns(specific_games)

# Generate insights
insights = analytics.generate_performance_insights(comparison_reports)
```

### 2. Command-Line Interface

#### Generate Reports

```bash
# Comprehensive performance report
python performance_report_cli.py --report

# Export data in different formats
python performance_report_cli.py --export json
python performance_report_cli.py --export csv --output my_analysis
python performance_report_cli.py --export html

# Analyze decision patterns
python performance_report_cli.py --patterns

# Generate insights
python performance_report_cli.py --insights

# Analyze specific games
python performance_report_cli.py --games game1 game2 --report

# Verbose output
python performance_report_cli.py --report --verbose
```

#### Batch Processing

```bash
# Generate all reports and exports
python performance_report_cli.py --report --patterns --insights --export html
```

### 3. Enhanced Web Interface

#### Starting the Interface

```bash
# Start enhanced web interface
python terminal_stream/enhanced_main.py

# Access at: http://127.0.0.1:5000
```

#### Features

- **Real-time Dashboard**: Live model performance indicators
- **Interactive Controls**: Clear output, toggle auto-scroll, export logs
- **Model Information**: Player and judge model assignments
- **Performance Metrics**: Decision counts, response times, success rates
- **Enhanced Output**: Syntax highlighting and categorized messages

### 4. Human Scoring Interface

#### Starting the Scoring Interface

```python
from web_human_scoring_integration import WebHumanScoringInterface

# Create and start interface
interface = WebHumanScoringInterface(web_port=5001)
interface.run_server()

# Access at: http://127.0.0.1:5001
```

#### Integration with Games

```python
from game import Game

# Create game with human scoring enabled
game = Game(
    player_configs=player_configs,
    judge_configs=judge_configs,
    enable_human_scoring=True,
    human_scoring_port=5001
)
```

### 5. Game Integration

#### Analytics Integration

```python
from game_analytics_integration import GameAnalyticsManager

# Create analytics manager
manager = GameAnalyticsManager()

# Start tracking
manager.start_game_session(game_record)

# Update during game
manager.update_session_progress(game_record)

# Record errors
manager.record_error_incident(
    model_name="gpt-4o",
    player_name="Alice",
    error_type="timeout",
    error_message="Response timeout"
)

# End session
session_analytics = manager.end_game_session(game_record, final_scores)

# Generate post-game report
report = manager.generate_post_game_report(
    game_record,
    display_report=True,
    export_formats=["json", "html"]
)
```

## 📊 Report Types

### 1. Model Comparison Report

- **Win Rates**: Percentage of games won by each model
- **Decision Metrics**: Total decisions, average response time
- **Challenge Analysis**: Success rates for challenges and defenses
- **Human Scores**: Average human evaluation scores
- **Performance Trends**: Historical performance data

### 2. Decision Pattern Analysis

- **Challenge Behavior**: Frequency and success of challenges made/received
- **Response Speed**: Distribution of decision times
- **Strategic Patterns**: Aggressive vs. conservative play styles
- **Interaction Rates**: Player-to-player interaction frequency

### 3. Performance Insights

- **Best Performers**: Highest win rates and human scores
- **Speed Analysis**: Fastest and slowest responding models
- **Specialization**: Best challengers and defenders
- **Consistency**: Performance variance across games

## 📤 Export Formats

### JSON Export

```json
{
  "export_timestamp": "2024-01-15T10:30:00",
  "models": {
    "gpt-4o": {
      "total_games": 10,
      "wins": 6,
      "win_rate": 0.6,
      "average_response_time": 2.3,
      "challenge_success_rate": 0.75,
      "human_score_average": 4.2
    }
  }
}
```

### CSV Export

```csv
model_name,total_games,wins,win_rate,total_decisions,average_response_time,challenge_success_rate,defense_success_rate,human_score_average,human_score_count
gpt-4o,10,6,0.600,45,2.300,0.750,0.800,4.200,20
claude-3-sonnet,10,4,0.400,42,1.800,0.600,0.900,4.100,18
```

### HTML Export

Interactive HTML reports with:

- Styled tables and charts
- Model performance summaries
- Responsive design
- Print-friendly formatting

## 🔧 Configuration

### Analytics Configuration

```python
# Custom directories
analytics = ModelPerformanceAnalytics(
    game_records_dir="custom_records",
    reports_dir="custom_reports"
)

# Custom export settings
analytics.export_performance_data(
    format_type="html",
    filename="quarterly_report",
    comparison_reports=reports
)
```

### Web Interface Configuration

```python
# Custom ports
interface = WebHumanScoringInterface(
    web_port=5001,
    main_web_port=5000
)

# Enhanced web interface
app.run(host='127.0.0.1', port=5000, threaded=True)
```

## 🎯 Example Workflows

### 1. Post-Game Analysis

```bash
# After running games, generate comprehensive analysis
python performance_report_cli.py --report --patterns --insights --export html
```

### 2. Real-time Monitoring

```bash
# Start enhanced web interface for live monitoring
python terminal_stream/enhanced_main.py
```

### 3. Human Evaluation Study

```python
# Run game with human scoring
game = Game(
    player_configs=configs,
    judge_configs=judges,
    enable_human_scoring=True,
    enable_analytics=True
)
game.start_game()
```

### 4. Historical Analysis

```bash
# Analyze specific time period or games
python performance_report_cli.py --games game_20240115_* --report --export csv
```

## 🐛 Troubleshooting

### Common Issues

1. **No Game Records Found**

   - Ensure games have been run and saved to `game_records/` directory
   - Check file permissions and paths

2. **Web Interface Not Loading**

   - Verify port 5000 is available
   - Check for firewall restrictions
   - Ensure Flask is installed

3. **Export Failures**

   - Check write permissions for `performance_reports/` directory
   - Verify sufficient disk space
   - Ensure valid filename characters

4. **Human Scoring Timeout**
   - Default timeout is 5 minutes
   - Increase timeout in configuration if needed
   - Check network connectivity

### Debug Mode

```bash
# Enable verbose logging
python performance_report_cli.py --report --verbose

# Check analytics system
python example_performance_reporting.py --analytics
```

## 🔮 Future Enhancements

- **Machine Learning Integration**: Predictive performance modeling
- **Advanced Visualizations**: Interactive charts and graphs
- **API Endpoints**: RESTful API for external integrations
- **Database Storage**: Persistent storage for large datasets
- **Real-time Alerts**: Performance threshold notifications
- **Comparative Studies**: Multi-session analysis tools

## 📞 Support

For issues or questions about the performance reporting system:

1. Check this documentation
2. Run the example script: `python example_performance_reporting.py`
3. Use verbose mode for detailed error information
4. Review the generated log files in `performance_reports/`

## 📄 License

This performance reporting system is part of the multi-LLM debate game project and follows the same licensing terms.
