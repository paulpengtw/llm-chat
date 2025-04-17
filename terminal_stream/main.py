from flask import Flask, render_template_string, Response
import threading
import time
import sys
import queue
from stream_handler import get_message_queue, init_stream

app = Flask(__name__)
messages = get_message_queue()

# HTML template with Server-Sent Events
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Terminal Output</title>
    <style>
        body {
            background-color: #1e1e1e;
            color: #ffffff;
            font-family: 'Courier New', monospace;
            margin: 0;
            padding: 20px;
        }
        #output {
            background-color: #000000;
            border-radius: 5px;
            padding: 15px;
            height: calc(100vh - 80px);
            overflow-y: auto;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        .line {
            margin: 0;
            padding: 2px 0;
        }
    </style>
</head>
<body>
    <div id="output"></div>
    <script>
        const output = document.getElementById('output');
        const eventSource = new EventSource('/stream');
        
        eventSource.onmessage = function(event) {
            const line = document.createElement('pre');
            line.className = 'line';
            line.innerHTML = event.data;
            if (event.data !== '\0') {  // Only append non-null messages
                output.appendChild(line);
            }
            output.scrollTop = output.scrollHeight;  // Always scroll on any message
        };
        
        eventSource.onerror = function() {
            const line = document.createElement('pre');
            line.className = 'line';
            line.style.color = '#ff6b6b';
            line.textContent = '--- Connection closed ---';
            output.appendChild(line);
        };
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/stream')
def stream():
    def generate():
        while True:
            try:
                message = messages.get(timeout=1)
                # Ensure the message is a string and handle any formatting
                if isinstance(message, (list, dict)):
                    message = str(message)
                # Escape special characters for proper HTML rendering
                message = message.replace('\n', '<br>').replace('═', '=').replace('★', '*').replace('─', '-')
                yield f"data: {message}\n\n"
                yield f"data: \0\n\n"  # Send null character to trigger scroll
            except queue.Empty:
                yield f"data: \0\n\n"  # Keep-alive message with null character

    return Response(generate(), mimetype='text/event-stream')

def run_game_thread():
    # Import here to avoid circular imports
    from game_runner import run_game
    time.sleep(2)  # Wait for server to start
    run_game()

def main():
    # Start game in a separate thread
    game_thread = threading.Thread(target=run_game_thread, daemon=True)
    game_thread.start()
    
    # Run the Flask app
    app.run(host='127.0.0.1', port=5000, threaded=True)

if __name__ == "__main__":
    main()
