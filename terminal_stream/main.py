from flask import Flask, render_template_string, Response
import sys
import io
import queue
import threading
import time

app = Flask(__name__)
# Make messages queue global and shared
messages = queue.Queue()
global_messages = messages  # For sharing across modules

# Custom stdout stream
class WebStream(io.TextIOBase):
    def write(self, text):
        if text and not text.isspace():
            global_messages.put(text)
        return len(text)

# Replace stdout with our custom stream
original_stdout = sys.stdout
sys.stdout = WebStream()

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
            line.textContent = event.data;
            output.appendChild(line);
            output.scrollTop = output.scrollHeight;
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
                yield f"data: {message}\n\n"
            except queue.Empty:
                yield f"data: \n\n"  # Keep-alive message

    return Response(generate(), mimetype='text/event-stream')

def test_output():
    time.sleep(2)  # Wait for server to start
    while True:
        print("Starting test output...")
        for i in range(5):
            print(f"Test line {i + 1}")
            time.sleep(1)
        print("Test complete!")
        time.sleep(3)  # Wait before next round

def main():
    # Start test output in a separate thread
    output_thread = threading.Thread(target=test_output, daemon=True)
    output_thread.start()
    
    # Run the Flask app
    app.run(host='127.0.0.1', port=5000, threaded=True)

if __name__ == "__main__":
    main()
