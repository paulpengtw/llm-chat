"""
Web Human Scoring Integration

This module provides integration between the human scoring interface and the web interface,
allowing human judges to score LLM performance through the web browser.
"""

from flask import Flask, render_template_string, request, jsonify, session
import threading
import time
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime
from human_scoring_interface import HumanScoringInterface


class WebHumanScoringInterface(HumanScoringInterface):
    """
    Enhanced human scoring interface that integrates with the web interface.
    
    This class extends the base HumanScoringInterface to provide:
    - Web-based scoring forms
    - Real-time score collection
    - Integration with the main web interface
    - Multi-judge support
    """
    
    def __init__(self, web_port: int = 5001, main_web_port: int = 5000):
        """
        Initialize the web human scoring interface.
        
        Args:
            web_port: Port for the scoring interface
            main_web_port: Port of the main web interface
        """
        super().__init__(web_port)
        self.main_web_port = main_web_port
        self.app = Flask(__name__)
        self.app.secret_key = str(uuid.uuid4())
        
        # Current scoring session data
        self.current_session: Optional[Dict[str, Any]] = None
        self.collected_scores: Dict[str, Dict[str, Dict[str, int]]] = {}
        self.session_timeout = 300  # 5 minutes
        
        self._setup_routes()
    
    def _setup_routes(self):
        """Set up Flask routes for the scoring interface"""
        
        @self.app.route('/')
        def scoring_home():
            """Main scoring interface page"""
            if not self.current_session:
                return render_template_string(WAITING_TEMPLATE)
            
            return render_template_string(
                SCORING_TEMPLATE,
                session_data=self.current_session,
                judge_id=session.get('judge_id', f'judge_{uuid.uuid4().hex[:8]}')
            )
        
        @self.app.route('/api/current_session')
        def api_current_session():
            """Get current scoring session data"""
            return jsonify({
                'active': self.current_session is not None,
                'session': self.current_session,
                'judge_id': session.get('judge_id')
            })
        
        @self.app.route('/api/submit_scores', methods=['POST'])
        def api_submit_scores():
            """Submit scores for the current session"""
            try:
                data = request.get_json()
                judge_id = session.get('judge_id', f'judge_{uuid.uuid4().hex[:8]}')
                session['judge_id'] = judge_id
                
                if not self.current_session:
                    return jsonify({'error': 'No active scoring session'}), 400
                
                # Validate scores
                scores = data.get('scores', {})
                if not scores:
                    return jsonify({'error': 'No scores provided'}), 400
                
                # Store scores
                if judge_id not in self.collected_scores:
                    self.collected_scores[judge_id] = {}
                
                self.collected_scores[judge_id] = scores
                
                # Update statistics
                self.statistics['completed_sessions'] += 1
                
                return jsonify({
                    'success': True,
                    'judge_id': judge_id,
                    'message': 'Scores submitted successfully'
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/session_status')
        def api_session_status():
            """Get current session status"""
            return jsonify({
                'active': self.current_session is not None,
                'judges_submitted': len(self.collected_scores),
                'timeout_remaining': self._get_timeout_remaining()
            })
    
    def start_scoring_session(self, round_info: Dict, players: List[str]) -> None:
        """
        Start a new scoring session.
        
        Args:
            round_info: Information about the round to be scored
            players: List of player names to score
        """
        self.current_session = {
            'session_id': str(uuid.uuid4()),
            'round_info': round_info,
            'players': players,
            'start_time': datetime.now().isoformat(),
            'criteria': [
                'strategic_thinking',
                'bluffing_skill', 
                'reasoning_quality',
                'overall_performance'
            ]
        }
        
        self.collected_scores = {}
        self.session_start_time = time.time()
        
        print(f"🌐 Human scoring session started: {self.current_session['session_id']}")
        print(f"   Access scoring interface at: http://127.0.0.1:{self.web_port}")
        print(f"   Players to score: {', '.join(players)}")
        
        # Update statistics
        self.statistics['total_sessions'] += 1
    
    def collect_scores(self, timeout: int = 300) -> Dict[str, Dict[str, int]]:
        """
        Collect scores from human judges.
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            Dict: Collected scores by player
        """
        if not self.current_session:
            return {}
        
        print(f"⏳ Collecting human scores (timeout: {timeout}s)...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.collected_scores:
                break
            time.sleep(1)
        
        # Process collected scores
        if self.collected_scores:
            # Aggregate scores from multiple judges
            aggregated_scores = self._aggregate_scores()
            
            # Calculate scoring time
            scoring_time = time.time() - self.session_start_time
            self.statistics['total_scoring_time'] += scoring_time
            
            print(f"✅ Human scores collected from {len(self.collected_scores)} judges")
            print(f"   Scoring time: {scoring_time:.1f}s")
            
            # End session
            self.current_session = None
            
            return aggregated_scores
        else:
            print("⏰ Human scoring timeout - no scores collected")
            self.statistics['timeout_sessions'] += 1
            self.current_session = None
            return {}
    
    def _aggregate_scores(self) -> Dict[str, Dict[str, int]]:
        """Aggregate scores from multiple judges"""
        if not self.collected_scores:
            return {}
        
        # For now, just use the first judge's scores
        # In a full implementation, you might average multiple judges
        first_judge_scores = list(self.collected_scores.values())[0]
        return first_judge_scores
    
    def _get_timeout_remaining(self) -> int:
        """Get remaining timeout in seconds"""
        if not hasattr(self, 'session_start_time'):
            return 0
        
        elapsed = time.time() - self.session_start_time
        remaining = max(0, self.session_timeout - elapsed)
        return int(remaining)
    
    def run_server(self):
        """Run the scoring interface server"""
        print(f"🌐 Starting Web Human Scoring Interface on port {self.web_port}")
        self.app.run(host='127.0.0.1', port=self.web_port, threaded=True, debug=False)


# HTML Templates

WAITING_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Human Scoring Interface</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            background: linear-gradient(135deg, #1e1e1e 0%, #2d2d2d 100%);
            color: #ffffff;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        
        .waiting-container {
            text-align: center;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 12px;
            padding: 40px;
            border: 1px solid #444;
            max-width: 500px;
        }
        
        .waiting-title {
            color: #FFC107;
            font-size: 24px;
            margin-bottom: 20px;
        }
        
        .waiting-message {
            color: #B0BEC5;
            font-size: 16px;
            line-height: 1.6;
        }
        
        .spinner {
            width: 40px;
            height: 40px;
            border: 4px solid #444;
            border-top: 4px solid #FFC107;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="waiting-container">
        <div class="waiting-title">👥 Human Scoring Interface</div>
        <div class="spinner"></div>
        <div class="waiting-message">
            Waiting for a scoring session to begin...<br><br>
            This interface will automatically update when a round is ready for human evaluation.
        </div>
    </div>
    
    <script>
        // Auto-refresh every 5 seconds to check for new sessions
        setInterval(() => {
            fetch('/api/current_session')
                .then(response => response.json())
                .then(data => {
                    if (data.active) {
                        location.reload();
                    }
                })
                .catch(error => console.log('Session check failed:', error));
        }, 5000);
    </script>
</body>
</html>
"""

SCORING_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Score LLM Performance</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            background: linear-gradient(135deg, #1e1e1e 0%, #2d2d2d 100%);
            color: #ffffff;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            min-height: 100vh;
        }
        
        .container {
            max-width: 1000px;
            margin: 0 auto;
        }
        
        .header {
            background: rgba(0, 0, 0, 0.3);
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            border: 1px solid #444;
        }
        
        .title {
            color: #FFC107;
            font-size: 24px;
            margin-bottom: 10px;
        }
        
        .round-info {
            color: #B0BEC5;
            font-size: 14px;
        }
        
        .players-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .player-card {
            background: rgba(0, 0, 0, 0.3);
            border-radius: 8px;
            padding: 20px;
            border: 1px solid #444;
        }
        
        .player-name {
            color: #4CAF50;
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 15px;
        }
        
        .criteria-group {
            margin-bottom: 15px;
        }
        
        .criteria-label {
            color: #ffffff;
            font-size: 14px;
            margin-bottom: 8px;
            display: block;
        }
        
        .score-buttons {
            display: flex;
            gap: 5px;
        }
        
        .score-btn {
            background: #444;
            color: #ffffff;
            border: none;
            padding: 8px 12px;
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.3s;
            font-size: 14px;
        }
        
        .score-btn:hover {
            background: #555;
        }
        
        .score-btn.selected {
            background: #4CAF50;
            color: #ffffff;
        }
        
        .submit-section {
            text-align: center;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 8px;
            padding: 20px;
            border: 1px solid #444;
        }
        
        .submit-btn {
            background: #4CAF50;
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
            transition: background 0.3s;
        }
        
        .submit-btn:hover {
            background: #45a049;
        }
        
        .submit-btn:disabled {
            background: #666;
            cursor: not-allowed;
        }
        
        .judge-info {
            color: #B0BEC5;
            font-size: 12px;
            margin-bottom: 15px;
        }
        
        .timeout-warning {
            background: rgba(255, 193, 7, 0.1);
            border: 1px solid #FFC107;
            border-radius: 4px;
            padding: 10px;
            margin-bottom: 20px;
            color: #FFC107;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="title">👥 Score LLM Performance</div>
            <div class="round-info">
                Round {{ session_data.round_info.round_id }} - Target Card: {{ session_data.round_info.target_card }}<br>
                Judge ID: {{ judge_id }}
            </div>
        </div>
        
        <div id="timeoutWarning" class="timeout-warning" style="display: none;">
            ⏰ Session will timeout in <span id="timeoutCounter">300</span> seconds
        </div>
        
        <form id="scoringForm">
            <div class="players-grid">
                {% for player in session_data.players %}
                <div class="player-card">
                    <div class="player-name">🤖 {{ player }}</div>
                    
                    {% for criterion in session_data.criteria %}
                    <div class="criteria-group">
                        <label class="criteria-label">{{ criterion.replace('_', ' ').title() }}</label>
                        <div class="score-buttons">
                            {% for score in range(6) %}
                            <button type="button" class="score-btn" 
                                    onclick="selectScore('{{ player }}', '{{ criterion }}', {{ score }})">
                                {{ score }}
                            </button>
                            {% endfor %}
                        </div>
                    </div>
                    {% endfor %}
                </div>
                {% endfor %}
            </div>
            
            <div class="submit-section">
                <div class="judge-info">
                    Please score each player on a scale of 0-5 for each criterion.<br>
                    0 = Poor, 1 = Below Average, 2 = Average, 3 = Good, 4 = Very Good, 5 = Excellent
                </div>
                <button type="button" class="submit-btn" onclick="submitScores()" disabled>
                    Submit Scores
                </button>
            </div>
        </form>
    </div>

    <script>
        const scores = {};
        const players = {{ session_data.players | tojsonfilter }};
        const criteria = {{ session_data.criteria | tojsonfilter }};
        let timeoutInterval;
        
        // Initialize scores object
        players.forEach(player => {
            scores[player] = {};
            criteria.forEach(criterion => {
                scores[player][criterion] = null;
            });
        });
        
        function selectScore(player, criterion, score) {
            scores[player][criterion] = score;
            
            // Update button appearance
            const buttons = document.querySelectorAll(`button[onclick*="${player}"][onclick*="${criterion}"]`);
            buttons.forEach((btn, index) => {
                btn.classList.toggle('selected', index === score);
            });
            
            checkFormCompletion();
        }
        
        function checkFormCompletion() {
            let allScored = true;
            
            for (const player of players) {
                for (const criterion of criteria) {
                    if (scores[player][criterion] === null) {
                        allScored = false;
                        break;
                    }
                }
                if (!allScored) break;
            }
            
            document.querySelector('.submit-btn').disabled = !allScored;
        }
        
        function submitScores() {
            fetch('/api/submit_scores', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ scores: scores })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Scores submitted successfully!');
                    // Redirect to waiting page
                    window.location.href = '/';
                } else {
                    alert('Error submitting scores: ' + data.error);
                }
            })
            .catch(error => {
                alert('Error submitting scores: ' + error);
            });
        }
        
        // Timeout countdown
        function startTimeoutCountdown() {
            let timeLeft = 300; // 5 minutes
            const counter = document.getElementById('timeoutCounter');
            const warning = document.getElementById('timeoutWarning');
            
            timeoutInterval = setInterval(() => {
                timeLeft--;
                counter.textContent = timeLeft;
                
                if (timeLeft <= 60) {
                    warning.style.display = 'block';
                }
                
                if (timeLeft <= 0) {
                    clearInterval(timeoutInterval);
                    alert('Session timed out!');
                    window.location.href = '/';
                }
            }, 1000);
        }
        
        // Start countdown on page load
        startTimeoutCountdown();
    </script>
</body>
</html>
"""


def create_web_human_scoring_demo():
    """Create a demo of the web human scoring interface"""
    print("🌐 Web Human Scoring Interface Demo")
    print("=" * 50)
    
    # Create interface
    interface = WebHumanScoringInterface(web_port=5001)
    
    # Start server in a separate thread
    server_thread = threading.Thread(target=interface.run_server, daemon=True)
    server_thread.start()
    
    print("Server started. Waiting for it to initialize...")
    time.sleep(2)
    
    # Simulate a scoring session
    round_info = {
        'round_id': 1,
        'target_card': 'K',
        'base_info': 'Demo round for testing',
        'action_info': 'Players made various moves...'
    }
    
    players = ['Alice', 'Bob', 'Charlie', 'Diana']
    
    print("Starting demo scoring session...")
    interface.start_scoring_session(round_info, players)
    
    print("Demo session active. You can now:")
    print(f"1. Open http://127.0.0.1:5001 to access the scoring interface")
    print("2. Score the players on the provided criteria")
    print("3. Submit your scores")
    
    # Collect scores (with timeout)
    scores = interface.collect_scores(timeout=60)  # 1 minute for demo
    
    if scores:
        print("Demo scores collected:")
        for player, player_scores in scores.items():
            avg_score = sum(player_scores.values()) / len(player_scores)
            print(f"  {player}: {avg_score:.1f}/5 average")
    else:
        print("No scores collected in demo")
    
    print("Demo completed!")


if __name__ == "__main__":
    create_web_human_scoring_demo()