"""
Human Scoring Interface for Multi-LLM Debate System

This module provides a web-based interface for human judges to score LLM performance
during card game rounds. It includes score collection, validation, and persistence.
"""

import json
import threading
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from flask import Flask, render_template_string, request, jsonify, Response
import queue
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ScoringSession:
    """Represents a single scoring session for a round"""
    session_id: str
    round_info: Dict[str, Any]
    players: List[str]
    scores: Dict[str, Dict[str, int]] = field(default_factory=dict)
    completed: bool = False
    timeout_seconds: int = 300
    start_time: float = field(default_factory=time.time)
    
    def is_expired(self) -> bool:
        """Check if the scoring session has expired"""
        return time.time() - self.start_time > self.timeout_seconds
    
    def is_complete(self) -> bool:
        """Check if all players have been scored"""
        return len(self.scores) == len(self.players) and all(
            len(player_scores) > 0 for player_scores in self.scores.values()
        )

class HumanScoringInterface:
    """Web-based interface for collecting human scores on LLM performance"""
    
    def __init__(self, web_port: int = 5001):
        """Initialize the human scoring interface
        
        Args:
            web_port: Port number for the web server
        """
        self.web_port = web_port
        self.app = Flask(__name__)
        self.app.logger.setLevel(logging.WARNING)  # Reduce Flask logging
        
        # Session management
        self.current_session: Optional[ScoringSession] = None
        self.session_lock = threading.Lock()
        self.server_thread: Optional[threading.Thread] = None
        self.server_running = False
        
        # Score collection queue for communication between web and game threads
        self.score_queue = queue.Queue()
        
        # Setup Flask routes
        self._setup_routes()
        
        # Statistics tracking
        self.scoring_statistics = {
            "total_sessions": 0,
            "completed_sessions": 0,
            "timeout_sessions": 0,
            "average_scoring_time": 0.0,
            "total_scoring_time": 0.0
        }
    
    def _setup_routes(self):
        """Setup Flask routes for the web interface"""
        
        @self.app.route('/')
        def home():
            """Main scoring interface page"""
            with self.session_lock:
                if not self.current_session:
                    return self._render_waiting_page()
                return self._render_scoring_page(self.current_session)
        
        @self.app.route('/api/session')
        def get_session():
            """API endpoint to get current session data"""
            with self.session_lock:
                if not self.current_session:
                    return jsonify({"error": "No active session"}), 404
                
                return jsonify({
                    "session_id": self.current_session.session_id,
                    "round_info": self.current_session.round_info,
                    "players": self.current_session.players,
                    "scores": self.current_session.scores,
                    "completed": self.current_session.completed,
                    "time_remaining": max(0, self.current_session.timeout_seconds - 
                                        (time.time() - self.current_session.start_time))
                })
        
        @self.app.route('/api/submit_score', methods=['POST'])
        def submit_score():
            """API endpoint to submit scores for a player"""
            try:
                data = request.get_json()
                player_name = data.get('player_name')
                scores = data.get('scores', {})
                
                if not player_name or not scores:
                    return jsonify({"error": "Missing player_name or scores"}), 400
                
                # Validate score values (0-5 scale)
                for criterion, score in scores.items():
                    if not isinstance(score, int) or score < 0 or score > 5:
                        return jsonify({
                            "error": f"Invalid score for {criterion}: must be integer 0-5"
                        }), 400
                
                with self.session_lock:
                    if not self.current_session:
                        return jsonify({"error": "No active session"}), 404
                    
                    if self.current_session.is_expired():
                        return jsonify({"error": "Session has expired"}), 408
                    
                    if player_name not in self.current_session.players:
                        return jsonify({"error": "Invalid player name"}), 400
                    
                    # Store the scores
                    self.current_session.scores[player_name] = scores
                    
                    # Check if session is complete
                    if self.current_session.is_complete():
                        self.current_session.completed = True
                        self.score_queue.put(self.current_session.scores)
                    
                    return jsonify({
                        "success": True,
                        "session_complete": self.current_session.completed
                    })
                    
            except Exception as e:
                logger.error(f"Error submitting score: {e}")
                return jsonify({"error": "Internal server error"}), 500
        
        @self.app.route('/api/statistics')
        def get_statistics():
            """API endpoint to get scoring statistics"""
            return jsonify(self.scoring_statistics)
    
    def _render_waiting_page(self) -> str:
        """Render the waiting page when no session is active"""
        return render_template_string("""
<!DOCTYPE html>
<html>
<head>
    <title>Human Scoring Interface</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 20px;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container {
            background: white;
            border-radius: 15px;
            padding: 40px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            text-align: center;
            max-width: 500px;
        }
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        h1 { color: #333; margin-bottom: 20px; }
        p { color: #666; font-size: 16px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Human Scoring Interface</h1>
        <div class="spinner"></div>
        <p>Waiting for a scoring session to begin...</p>
        <p>This page will automatically update when a round is ready for scoring.</p>
    </div>
    <script>
        // Auto-refresh every 3 seconds to check for new sessions
        setTimeout(() => location.reload(), 3000);
    </script>
</body>
</html>
        """)
    
    def _render_scoring_page(self, session: ScoringSession) -> str:
        """Render the main scoring interface page"""
        return render_template_string("""
<!DOCTYPE html>
<html>
<head>
    <title>Score LLM Performance - Round {{ session.round_info.get('round_id', 'N/A') }}</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 20px;
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #eee;
        }
        .timer {
            background: #ff6b6b;
            color: white;
            padding: 10px 20px;
            border-radius: 25px;
            display: inline-block;
            font-weight: bold;
            margin-top: 10px;
        }
        .round-info {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 30px;
        }
        .round-info h3 {
            margin-top: 0;
            color: #333;
        }
        .players-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .player-card {
            border: 2px solid #ddd;
            border-radius: 10px;
            padding: 20px;
            background: #fafafa;
            transition: all 0.3s ease;
        }
        .player-card.scored {
            border-color: #28a745;
            background: #f8fff9;
        }
        .player-card h4 {
            margin-top: 0;
            color: #333;
            font-size: 18px;
        }
        .scoring-criteria {
            margin: 15px 0;
        }
        .criterion {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin: 10px 0;
            padding: 10px;
            background: white;
            border-radius: 5px;
        }
        .criterion label {
            font-weight: 500;
            color: #555;
        }
        .score-buttons {
            display: flex;
            gap: 5px;
        }
        .score-btn {
            width: 35px;
            height: 35px;
            border: 2px solid #ddd;
            background: white;
            border-radius: 50%;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.2s ease;
        }
        .score-btn:hover {
            background: #667eea;
            color: white;
            border-color: #667eea;
        }
        .score-btn.selected {
            background: #28a745;
            color: white;
            border-color: #28a745;
        }
        .submit-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
            transition: all 0.3s ease;
            width: 100%;
            margin-top: 15px;
        }
        .submit-btn:hover {
            background: #5a6fd8;
            transform: translateY(-2px);
        }
        .submit-btn:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
        }
        .completion-message {
            text-align: center;
            padding: 30px;
            background: #d4edda;
            border-radius: 10px;
            color: #155724;
            font-size: 18px;
            font-weight: bold;
        }
        .progress-bar {
            width: 100%;
            height: 20px;
            background: #eee;
            border-radius: 10px;
            overflow: hidden;
            margin: 20px 0;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #28a745, #20c997);
            transition: width 0.3s ease;
        }
        @media (max-width: 768px) {
            .players-grid {
                grid-template-columns: 1fr;
            }
            .container {
                padding: 15px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Human Scoring Interface</h1>
            <h2>Round {{ session.round_info.get('round_id', 'N/A') }} Evaluation</h2>
            <div class="timer" id="timer">Time remaining: <span id="time-display">{{ session.timeout_seconds }}</span>s</div>
            <div class="progress-bar">
                <div class="progress-fill" id="progress-fill" style="width: 0%"></div>
            </div>
        </div>

        <div class="round-info">
            <h3>Round Information</h3>
            <p><strong>Target Card:</strong> {{ session.round_info.get('target_card', 'N/A') }}</p>
            <p><strong>Players:</strong> {{ ', '.join(session.players) }}</p>
            {% if session.round_info.get('starting_player') %}
            <p><strong>Starting Player:</strong> {{ session.round_info.get('starting_player') }}</p>
            {% endif %}
        </div>

        <div id="scoring-interface">
            <div class="players-grid" id="players-grid">
                {% for player in session.players %}
                <div class="player-card" id="card-{{ player }}">
                    <h4>{{ player }}</h4>
                    <div class="scoring-criteria">
                        <div class="criterion">
                            <label>Strategic Thinking:</label>
                            <div class="score-buttons" data-player="{{ player }}" data-criterion="strategic_thinking">
                                {% for score in range(6) %}
                                <button class="score-btn" data-score="{{ score }}">{{ score }}</button>
                                {% endfor %}
                            </div>
                        </div>
                        <div class="criterion">
                            <label>Bluffing Skill:</label>
                            <div class="score-buttons" data-player="{{ player }}" data-criterion="bluffing_skill">
                                {% for score in range(6) %}
                                <button class="score-btn" data-score="{{ score }}">{{ score }}</button>
                                {% endfor %}
                            </div>
                        </div>
                        <div class="criterion">
                            <label>Reasoning Quality:</label>
                            <div class="score-buttons" data-player="{{ player }}" data-criterion="reasoning_quality">
                                {% for score in range(6) %}
                                <button class="score-btn" data-score="{{ score }}">{{ score }}</button>
                                {% endfor %}
                            </div>
                        </div>
                        <div class="criterion">
                            <label>Overall Performance:</label>
                            <div class="score-buttons" data-player="{{ player }}" data-criterion="overall_performance">
                                {% for score in range(6) %}
                                <button class="score-btn" data-score="{{ score }}">{{ score }}</button>
                                {% endfor %}
                            </div>
                        </div>
                    </div>
                    <button class="submit-btn" onclick="submitPlayerScore('{{ player }}')" disabled>
                        Submit Score for {{ player }}
                    </button>
                </div>
                {% endfor %}
            </div>
        </div>

        <div id="completion-message" class="completion-message" style="display: none;">
            <h3>✅ Scoring Complete!</h3>
            <p>All player scores have been submitted successfully.</p>
            <p>The game will continue automatically.</p>
        </div>
    </div>

    <script>
        let playerScores = {};
        let timeRemaining = {{ session.timeout_seconds }};
        let totalPlayers = {{ session.players|length }};
        let scoredPlayers = 0;

        // Initialize player scores object
        {% for player in session.players %}
        playerScores['{{ player }}'] = {};
        {% endfor %}

        // Timer functionality
        function updateTimer() {
            const display = document.getElementById('time-display');
            const progressFill = document.getElementById('progress-fill');
            
            if (timeRemaining <= 0) {
                display.textContent = '0';
                document.getElementById('timer').style.background = '#dc3545';
                document.getElementById('timer').innerHTML = '<strong>⏰ TIME EXPIRED</strong>';
                disableAllInputs();
                return;
            }
            
            display.textContent = timeRemaining;
            
            // Update progress bar
            const progress = (scoredPlayers / totalPlayers) * 100;
            progressFill.style.width = progress + '%';
            
            // Change timer color based on time remaining
            const timer = document.getElementById('timer');
            if (timeRemaining < 60) {
                timer.style.background = '#dc3545';
            } else if (timeRemaining < 120) {
                timer.style.background = '#ffc107';
                timer.style.color = '#000';
            }
            
            timeRemaining--;
            setTimeout(updateTimer, 1000);
        }

        // Score button functionality
        document.addEventListener('click', function(e) {
            if (e.target.classList.contains('score-btn')) {
                const player = e.target.parentElement.dataset.player;
                const criterion = e.target.parentElement.dataset.criterion;
                const score = parseInt(e.target.dataset.score);
                
                // Remove selected class from siblings
                e.target.parentElement.querySelectorAll('.score-btn').forEach(btn => {
                    btn.classList.remove('selected');
                });
                
                // Add selected class to clicked button
                e.target.classList.add('selected');
                
                // Store score
                if (!playerScores[player]) {
                    playerScores[player] = {};
                }
                playerScores[player][criterion] = score;
                
                // Check if all criteria for this player are scored
                const requiredCriteria = ['strategic_thinking', 'bluffing_skill', 'reasoning_quality', 'overall_performance'];
                const playerComplete = requiredCriteria.every(c => playerScores[player][c] !== undefined);
                
                // Enable/disable submit button
                const submitBtn = document.querySelector(`#card-${player} .submit-btn`);
                submitBtn.disabled = !playerComplete;
            }
        });

        // Submit score for a player
        function submitPlayerScore(player) {
            const scores = playerScores[player];
            
            fetch('/api/submit_score', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    player_name: player,
                    scores: scores
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Mark player card as completed
                    const card = document.getElementById(`card-${player}`);
                    card.classList.add('scored');
                    card.querySelector('.submit-btn').textContent = '✅ Score Submitted';
                    card.querySelector('.submit-btn').disabled = true;
                    card.querySelector('.submit-btn').style.background = '#28a745';
                    
                    scoredPlayers++;
                    
                    // Check if all players are scored
                    if (data.session_complete) {
                        document.getElementById('scoring-interface').style.display = 'none';
                        document.getElementById('completion-message').style.display = 'block';
                    }
                } else {
                    alert('Error submitting score: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error submitting score. Please try again.');
            });
        }

        function disableAllInputs() {
            document.querySelectorAll('.score-btn, .submit-btn').forEach(el => {
                el.disabled = true;
                el.style.cursor = 'not-allowed';
                el.style.opacity = '0.5';
            });
        }

        // Start timer
        updateTimer();
    </script>
</body>
</html>
        """, session=session)
    
    def start_server(self):
        """Start the web server in a separate thread"""
        if self.server_running:
            return
        
        def run_server():
            self.server_running = True
            try:
                self.app.run(host='127.0.0.1', port=self.web_port, 
                           threaded=True, debug=False, use_reloader=False)
            except Exception as e:
                logger.error(f"Error running web server: {e}")
            finally:
                self.server_running = False
        
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        
        # Wait a moment for server to start
        time.sleep(1)
        logger.info(f"Human scoring interface started at http://127.0.0.1:{self.web_port}")
    
    def stop_server(self):
        """Stop the web server"""
        self.server_running = False
        if self.server_thread and self.server_thread.is_alive():
            self.server_thread.join(timeout=2)
    
    def start_scoring_session(self, round_info: Dict, players: List[str], timeout: int = 300) -> None:
        """Start a new scoring session for a round
        
        Args:
            round_info: Information about the round being scored
            players: List of player names to score
            timeout: Timeout in seconds for the scoring session
        """
        session_id = f"round_{round_info.get('round_id', int(time.time()))}"
        
        with self.session_lock:
            self.current_session = ScoringSession(
                session_id=session_id,
                round_info=round_info,
                players=players,
                timeout_seconds=timeout
            )
        
        self.scoring_statistics["total_sessions"] += 1
        
        # Start server if not already running
        if not self.server_running:
            self.start_server()
        
        logger.info(f"Started scoring session {session_id} for players: {players}")
        logger.info(f"Scoring interface available at: http://127.0.0.1:{self.web_port}")
    
    def collect_scores(self, timeout: int = 300) -> Dict[str, Dict[str, int]]:
        """Collect scores from the current session
        
        Args:
            timeout: Maximum time to wait for scores in seconds
            
        Returns:
            Dictionary mapping player names to their scores
        """
        if not self.current_session:
            logger.warning("No active scoring session")
            return {}
        
        start_time = time.time()
        
        try:
            # Wait for scores to be submitted
            while time.time() - start_time < timeout:
                try:
                    # Check if scores are available
                    scores = self.score_queue.get(timeout=1)
                    
                    # Update statistics
                    scoring_time = time.time() - self.current_session.start_time
                    self.scoring_statistics["completed_sessions"] += 1
                    self.scoring_statistics["total_scoring_time"] += scoring_time
                    self.scoring_statistics["average_scoring_time"] = (
                        self.scoring_statistics["total_scoring_time"] / 
                        self.scoring_statistics["completed_sessions"]
                    )
                    
                    logger.info(f"Collected scores for session {self.current_session.session_id}")
                    return scores
                    
                except queue.Empty:
                    # Check if session expired
                    with self.session_lock:
                        if self.current_session and self.current_session.is_expired():
                            self.scoring_statistics["timeout_sessions"] += 1
                            logger.warning(f"Scoring session {self.current_session.session_id} expired")
                            return self.current_session.scores  # Return partial scores
                    continue
            
            # Timeout reached
            self.scoring_statistics["timeout_sessions"] += 1
            logger.warning("Score collection timeout reached")
            with self.session_lock:
                return self.current_session.scores if self.current_session else {}
                
        finally:
            # Clean up session
            with self.session_lock:
                self.current_session = None
    
    def display_round_summary(self, round_info: Dict, ai_votes: Dict, human_scores: Dict) -> None:
        """Display a summary of round evaluation results
        
        Args:
            round_info: Information about the round
            ai_votes: AI judge votes
            human_scores: Human judge scores
        """
        print("\n" + "="*60)
        print(f"ROUND {round_info.get('round_id', 'N/A')} EVALUATION SUMMARY")
        print("="*60)
        
        print(f"Target Card: {round_info.get('target_card', 'N/A')}")
        print(f"Players: {', '.join(round_info.get('round_players', []))}")
        
        print("\nAI JUDGE VOTES:")
        print("-" * 30)
        for judge_name, vote_info in ai_votes.get('votes', {}).items():
            voted_player = vote_info.get('voted_player', 'None')
            reasoning = vote_info.get('reasoning', 'No reasoning provided')
            print(f"{judge_name}: {voted_player}")
            print(f"  Reasoning: {reasoning[:100]}{'...' if len(reasoning) > 100 else ''}")
        
        print("\nHUMAN JUDGE SCORES:")
        print("-" * 30)
        if human_scores:
            for player_name, scores in human_scores.items():
                print(f"{player_name}:")
                for criterion, score in scores.items():
                    criterion_display = criterion.replace('_', ' ').title()
                    print(f"  {criterion_display}: {score}/5")
                
                # Calculate average score
                avg_score = sum(scores.values()) / len(scores) if scores else 0
                print(f"  Average: {avg_score:.1f}/5")
                print()
        else:
            print("No human scores collected")
        
        print("="*60)
    
    def get_scoring_statistics(self) -> Dict:
        """Get statistics about scoring sessions
        
        Returns:
            Dictionary containing scoring statistics
        """
        return self.scoring_statistics.copy()