import io
import queue
import sys
import threading
from typing import Optional

# Global message queue
global_messages = queue.Queue()

class WebStream(io.TextIOBase):
    """A custom stream that captures output and sends it to a queue"""
    def write(self, text) -> int:
        if isinstance(text, bytes):
            text = text.decode('utf-8')
            
        if text and not text.isspace():
            # Split text by newlines and send each line separately
            lines = text.split('\n')
            for line in lines:
                if line and not line.isspace():
                    global_messages.put(line + '\n')
        return len(str(text))

    def flush(self) -> None:
        pass

# Create a global instance of WebStream
_stream_instance: Optional[WebStream] = None
_original_stdout = sys.stdout

def init_stream() -> None:
    """Initialize the stream handler and redirect stdout"""
    global _stream_instance
    if _stream_instance is None:
        _stream_instance = WebStream()
        sys.stdout = _stream_instance

def restore_stdout() -> None:
    """Restore the original stdout"""
    sys.stdout = _original_stdout

def get_message_queue() -> queue.Queue:
    """Get the global message queue"""
    return global_messages

# Initialize stream on module import
init_stream()
