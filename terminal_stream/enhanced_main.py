"""
Enhanced Flask Web Interface for Multi-LLM Debate Games

This module provides an enhanced web interface that displays:
- Real-time game output with model information
- Model performance indicators
- Human scoring interface integration
- Live analytics dashboard
"""

from flask import Flask, render_template_string, Response, request, jsonify
import threading
import time
import sys
import queue
import json
from datetime import datetime
from typing import Dict, Any, Optional
from stream_handler import get_message_queue, init_stream

app = Flask(__name__)
messages = get_message_queue()

# Global state for game information
game_state = {
    "players": {},
    "judges": {},
    "current_round": 0,
    "game_id": "",
    "analytics": {},
    "human_scoring_active": False
}

# Enhanced HTML template with model information display
ENHANCED_HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Multi-LLM Debate Game - Live Stream</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            background: linear-gradient(135deg, #1e1e1e 0%, #2d2d2d 100%);
            color: #ffffff;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            height: 100vh;
            overflow: hidden;
        }
        
        .container {
            display: grid;
            grid-template-columns: 300px 1fr 300px;
            grid-template-rows: 60px 1fr;
            height: 100vh;
            gap: 10px;
            padding: 10px;
        }
        
        .header {
            grid-column: 1 / -1;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 8px;
            padding: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border: 1px solid #444;
        }
        
        .game-info {
            display: flex;
            align-items: center;
            gap: 20px;
        }
        
        .game-id {
            font-weight: bold;
            color: #4CAF50;
        }
        
        .round-info {
            color: #FFC107;
        }
        
        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #4CAF50;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .sidebar {
            background: rgba(0, 0, 0, 0.3);
            border-radius: 8px;
            padding: 15px;
            border: 1px solid #444;
            overflow-y: auto;
        }
        
        .sidebar h3 {
            color: #4CAF50;
            margin-bottom: 15px;
            font-size: 16px;
            border-bottom: 1px solid #444;
            padding-bottom: 8px;
        }
        
        .player-card, .judge-card {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 6px;
            padding: 12px;
            margin-bottom: 10px;
            border-left: 3px solid #4CAF50;
        }
        
        .player-name, .judge-name {
            font-weight: bold;
            color: #ffffff;
            margin-bottom: 4px;
        }
        
        .model-name {
            color: #81C784;
            font-size: 12px;
            margin-bottom: 8px;
        }
        
        .performance-stats {
            font-size: 11px;
            color: #B0BEC5;
        }
        
        .stat-row {
            display: flex;
            justify-content: space-between;
            margin-bottom: 2px;
        }
        
        .main-content {
            background: rgba(0, 0, 0, 0.5);
            border-radius: 8px;
            padding: 15px;
            border: 1px solid #444;
            display: flex;
            flex-direction: column;
        }
        
        .output-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
            padding-bottom: 10px;
            border-bottom: 1px solid #444;
        }
        
        .output-title {
            color: #4CAF50;
            font-weight: bold;
        }
        
        .output-controls {
            display: flex;
            gap: 10px;
        }
        
        .btn {
            background: #4CAF50;
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            transition: background 0.3s;
        }
        
        .btn:hover {
            background: #45a049;
        }
        
        .btn.secondary {
            background: #757575;
        }
        
        .btn.secondary:hover {
            background: #616161;
        }
        
        #output {
            background-color: #000000;
            border-radius: 5px;
            padding: 15px;
            flex: 1;
            overflow-y: auto;
            white-space: pre-wrap;
            word-wrap: break-word;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            line-height: 1.4;
        }
        
        .line {
            margin: 0;
            padding: 1px 0;
        }
        
        .model-highlight {
            background: rgba(76, 175, 80, 0.2);
            padding: 2px 4px;
            border-radius: 3px;
        }
        
        .player-action {
            color: #81C784;
        }
        
        .judge-action {
            color: #FFB74D;
        }
        
        .error-message {
            color: #F44336;
        }
        
        .success-message {
            color: #4CAF50;
        }
        
        .analytics-panel {
            max-height: 300px;
            overflow-y: auto;
        }
        
        .metric-card {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 4px;
            padding: 8px;
            margin-bottom: 8px;
        }
        
        .metric-label {
            font-size: 11px;
            color: #B0BEC5;
            margin-bottom: 2px;
        }
        
        .metric-value {
            font-weight: bold;
            color: #ffffff;
        }
        
        .human-scoring-panel {
            background: rgba(255, 193, 7, 0.1);
            border: 1px solid #FFC107;
            border-radius: 6px;
            padding: 10px;
            margin-top: 10px;
        }
        
        .human-scoring-title {
            color: #FFC107;
            font-weight: bold;
            margin-bottom: 8px;
        }
        
        .scrollbar-custom::-webkit-scrollbar {
            width: 6px;
        }
        
        .scrollbar-custom::-webkit-scrollbar-track {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 3px;
        }
        
        .scrollbar-custom::-webkit-scrollbar-thumb {
            background: #4CAF50;
            border-radius: 3px;
        }
        
        .scrollbar-custom::-webkit-scrollbar-thumb:hover {
            background: #45a049;
        }
        
        @media (max-width: 1200px) {
            .container {
                grid-template-columns: 250px 1fr 250px;
            }
        }
        
        @media (max-width: 900px) {
            .container {
                grid-template-columns: 1fr;
                grid-template-rows: auto auto 1fr;
            }
            
            .sidebar {
                max-height: 200px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="game-info">
                <div class="status-indicator"></div>
                <div class="game-id" id="gameId">Game: Loading...</div>
                <div class="round-info" id="roundInfo">Round: -</div>
            </div>
            <div class="output-controls">
                <button class="btn" onclick="clearOutput()">Clear</button>
                <button class="btn secondary" onclick="toggleAutoScroll()">Auto-scroll: ON</button>
                <button class="btn secondary" onclick="exportLog()">Export</button>
            </div>
        </div>
        
        <div class="sidebar scrollbar-custom">
            <h3>🎮 Players</h3>
            <div id="playersPanel">
                <div class="player-card">
                    <div class="player-name">Loading players...</div>
                </div>
            </div>
            
            <h3>⚖️ Judges</h3>
            <div id="judgesPanel">
                <div class="judge-card">
                    <div class="judge-name">Loading judges...</div>
                </div>
            </div>
        </div>
        
        <div class="main-content">
            <div class="output-header">
                <div class="output-title">🎯 Game Output</div>
            </div>
            <div id="output" class="scrollbar-custom"></div>
        </div>
        
        <div class="sidebar scrollbar-custom">
            <h3>📊 Live Analytics</h3>
            <div id="analyticsPanel" class="analytics-panel">
                <div class="metric-card">
                    <div class="metric-label">Total Decisions</div>
                    <div class="metric-value" id="totalDecisions">0</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Session Duration</div>
                    <div class="metric-value" id="sessionDuration">0:00</div>
                </div>
            </div>
            
            <div id="humanScoringPanel" class="human-scoring-panel" style="display: none;">
                <div class="human-scoring-title">👥 Human Scoring Active</div>
                <div id="humanScoringStatus">Waiting for scores...</div>
            </div>
        </div>
    </div>

    <script>
        let autoScroll = true;
        let startTime = Date.now();
        
        const output = document.getElementById('output');
        const eventSource = new EventSource('/stream');
        
        // Game state update handler
        eventSource.addEventListener('game_state', function(event) {
            const gameState = JSON.parse(event.data);
            updateGameState(gameState);
        });
        
        // Regular message handler
        eventSource.onmessage = function(event) {
            if (event.data === '\\0') {
                if (autoScroll) {
                    output.scrollTop = output.scrollHeight;
                }
                return;
            }
            
            const line = document.createElement('pre');
            line.className = 'line';
            
            // Enhanced message processing with model highlighting
            let processedMessage = event.data;
            processedMessage = highlightModelNames(processedMessage);
            processedMessage = highlightPlayerActions(processedMessage);
            
            line.innerHTML = processedMessage;
            output.appendChild(line);
            
            if (autoScroll) {
                output.scrollTop = output.scrollHeight;
            }
        };
        
        eventSource.onerror = function() {
            const line = document.createElement('pre');
            line.className = 'line error-message';
            line.textContent = '--- Connection lost - Attempting to reconnect ---';
            output.appendChild(line);
        };
        
        function highlightModelNames(message) {
            // Highlight common model names
            const modelPatterns = [
                /\\b(gpt-4o|gpt-4o-mini|claude-3-sonnet|claude-3-haiku|deepseek-r1)\\b/gi,
                /\\((gpt-4o|gpt-4o-mini|claude-3-sonnet|claude-3-haiku|deepseek-r1)\\)/gi
            ];
            
            modelPatterns.forEach(pattern => {
                message = message.replace(pattern, '<span class="model-highlight">$1</span>');
            });
            
            return message;
        }
        
        function highlightPlayerActions(message) {
            // Highlight player actions
            if (message.includes("'s turn") || message.includes("played") || message.includes("challenged")) {
                return '<span class="player-action">' + message + '</span>';
            }
            
            // Highlight judge actions
            if (message.includes("Judge") || message.includes("voted")) {
                return '<span class="judge-action">' + message + '</span>';
            }
            
            // Highlight errors
            if (message.includes("Error") || message.includes("Failed") || message.includes("timeout")) {
                return '<span class="error-message">' + message + '</span>';
            }
            
            // Highlight success messages
            if (message.includes("won") || message.includes("successful") || message.includes("✓")) {
                return '<span class="success-message">' + message + '</span>';
            }
            
            return message;
        }
        
        function updateGameState(gameState) {
            // Update header information
            document.getElementById('gameId').textContent = `Game: ${gameState.game_id || 'Unknown'}`;
            document.getElementById('roundInfo').textContent = `Round: ${gameState.current_round || 0}`;
            
            // Update players panel
            updatePlayersPanel(gameState.players || {});
            
            // Update judges panel
            updateJudgesPanel(gameState.judges || {});
            
            // Update analytics
            updateAnalytics(gameState.analytics || {});
            
            // Update human scoring status
            updateHumanScoringStatus(gameState.human_scoring_active || false);
        }
        
        function updatePlayersPanel(players) {
            const panel = document.getElementById('playersPanel');
            panel.innerHTML = '';
            
            Object.entries(players).forEach(([name, info]) => {
                const card = document.createElement('div');
                card.className = 'player-card';
                card.innerHTML = `
                    <div class="player-name">${name}</div>
                    <div class="model-name">🤖 ${info.model || 'Unknown'}</div>
                    <div class="performance-stats">
                        <div class="stat-row">
                            <span>Decisions:</span>
                            <span>${info.decisions || 0}</span>
                        </div>
                        <div class="stat-row">
                            <span>Avg Time:</span>
                            <span>${(info.avg_response_time || 0).toFixed(2)}s</span>
                        </div>
                        <div class="stat-row">
                            <span>Challenge Rate:</span>
                            <span>${((info.challenge_success_rate || 0) * 100).toFixed(1)}%</span>
                        </div>
                    </div>
                `;
                panel.appendChild(card);
            });
        }
        
        function updateJudgesPanel(judges) {
            const panel = document.getElementById('judgesPanel');
            panel.innerHTML = '';
            
            Object.entries(judges).forEach(([name, info]) => {
                const card = document.createElement('div');
                card.className = 'judge-card';
                card.innerHTML = `
                    <div class="judge-name">${name}</div>
                    <div class="model-name">🤖 ${info.model || 'Unknown'}</div>
                `;
                panel.appendChild(card);
            });
        }
        
        function updateAnalytics(analytics) {
            document.getElementById('totalDecisions').textContent = analytics.total_decisions || 0;
            
            // Update session duration
            const duration = Math.floor((Date.now() - startTime) / 1000);
            const minutes = Math.floor(duration / 60);
            const seconds = duration % 60;
            document.getElementById('sessionDuration').textContent = 
                `${minutes}:${seconds.toString().padStart(2, '0')}`;
        }
        
        function updateHumanScoringStatus(isActive) {
            const panel = document.getElementById('humanScoringPanel');
            if (isActive) {
                panel.style.display = 'block';
            } else {
                panel.style.display = 'none';
            }
        }
        
        function clearOutput() {
            output.innerHTML = '';
        }
        
        function toggleAutoScroll() {
            autoScroll = !autoScroll;
            const btn = event.target;
            btn.textContent = `Auto-scroll: ${autoScroll ? 'ON' : 'OFF'}`;
        }
        
        function exportLog() {
            const logContent = output.textContent;
            const blob = new Blob([logContent], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `game_log_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.txt`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }
        
        // Periodic analytics update
        setInterval(() => {
            fetch('/api/game_state')
                .then(response => response.json())
                .then(data => updateGameState(data))
                .catch(error => console.log('Analytics update failed:', error));
        }, 5000);
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(ENHANCED_HTML_TEMPLATE)

@app.route('/stream')
def stream():
    def generate():
        while True:
            try:
                message = messages.get(timeout=1)
                
                # Handle different message types
                if isinstance(message, dict):
                    if message.get('type') == 'game_state':
                        yield f"event: game_state\ndata: {json.dumps(message['data'])}\n\n"
                        continue
                    else:
                        message = json.dumps(message)
                elif isinstance(message, (list, tuple)):
                    message = str(message)
                
                # Process regular messages
                if message:
                    # Escape special characters for proper HTML rendering
                    message = message.replace('\n', '<br>')
                    message = message.replace('═', '=').replace('★', '*').replace('─', '-')
                    yield f"data: {message}\n\n"
                
                # Send keep-alive
                yield f"data: \\0\n\n"
                
            except queue.Empty:
                yield f"data: \\0\n\n"  # Keep-alive message

    return Response(generate(), mimetype='text/event-stream')

@app.route('/api/game_state')
def api_game_state():
    """API endpoint for getting current game state"""
    return jsonify(game_state)

@app.route('/api/update_game_state', methods=['POST'])
def api_update_game_state():
    """API endpoint for updating game state"""
    global game_state
    try:
        data = request.get_json()
        if data:
            game_state.update(data)
            
            # Send game state update to stream
            state_message = {
                'type': 'game_state',
                'data': game_state
            }
            messages.put(state_message)
            
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/human_scoring_status', methods=['POST'])
def api_human_scoring_status():
    """API endpoint for updating human scoring status"""
    global game_state
    try:
        data = request.get_json()
        game_state['human_scoring_active'] = data.get('active', False)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

def update_game_state_from_game(game_record, analytics_manager=None):
    """
    Update the web interface game state from a game record.
    
    Args:
        game_record: Current game record
        analytics_manager: Optional analytics manager for real-time stats
    """
    global game_state
    
    # Update basic game info
    game_state['game_id'] = game_record.game_id
    game_state['current_round'] = len(game_record.rounds)
    
    # Update player information
    players = {}
    for player_name, model_name in game_record.player_model_assignments.items():
        perf_key = game_record.get_model_performance_key(player_name)
        perf_record = game_record.model_performance.get(perf_key)
        
        players[player_name] = {
            'model': model_name,
            'decisions': perf_record.decision_count if perf_record else 0,
            'avg_response_time': perf_record.average_response_time if perf_record else 0.0,
            'challenge_success_rate': perf_record.challenge_success_rate if perf_record else 0.0,
            'defense_success_rate': perf_record.defense_success_rate if perf_record else 0.0
        }
    
    game_state['players'] = players
    
    # Update judge information
    judges = {}
    for judge_name, model_name in game_record.judge_model_assignments.items():
        judges[judge_name] = {
            'model': model_name
        }
    
    game_state['judges'] = judges
    
    # Update analytics
    if analytics_manager:
        real_time_stats = analytics_manager.get_real_time_statistics(game_record)
        game_state['analytics'] = {
            'total_decisions': real_time_stats.get('total_decisions', 0),
            'session_duration': real_time_stats.get('session_duration', 0.0),
            'current_round': real_time_stats.get('current_round', 0)
        }
    else:
        game_state['analytics'] = {
            'total_decisions': sum(perf.decision_count for perf in game_record.model_performance.values()),
            'session_duration': 0.0,
            'current_round': len(game_record.rounds)
        }
    
    # Send update to web interface
    state_message = {
        'type': 'game_state',
        'data': game_state.copy()
    }
    messages.put(state_message)

def run_game_thread():
    """Run game in a separate thread"""
    # Import here to avoid circular imports
    from game_runner import run_enhanced_game
    time.sleep(2)  # Wait for server to start
    run_enhanced_game()

def main():
    """Main function to start the enhanced web interface"""
    print("Starting Enhanced Multi-LLM Debate Game Web Interface...")
    print("Features:")
    print("  - Real-time model performance indicators")
    print("  - Live analytics dashboard")
    print("  - Enhanced game output with model highlighting")
    print("  - Human scoring interface integration")
    print()
    print("Access the interface at: http://127.0.0.1:5000")
    print()
    
    # Start game in a separate thread
    game_thread = threading.Thread(target=run_game_thread, daemon=True)
    game_thread.start()
    
    # Run the Flask app
    app.run(host='127.0.0.1', port=5000, threaded=True, debug=False)

if __name__ == "__main__":
    main()