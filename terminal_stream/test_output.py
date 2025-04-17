import time
from main import WebStream, global_messages
import sys

def main():
    # Create a new WebStream instance that uses the global queue
    custom_stream = WebStream()
    sys.stdout = custom_stream
    
    print("Starting test output...")
    for i in range(5):
        print(f"Test line {i + 1}")
        time.sleep(1)
    print("Test complete!")

if __name__ == "__main__":
    main()
