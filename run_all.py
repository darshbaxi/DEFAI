import os
import threading
import time
import requests

def wait_for_zerepy(url="http://localhost:8000/connections", retries=10, delay=3):
    for _ in range(retries):
        try:
            res = requests.get(url)
            if res.ok:
                print("ZerePy server is ready!")
                return True
        except requests.ConnectionError:
            print("Waiting for ZerePy to start...")
            time.sleep(delay)
    return False

def start_servers():
    threading.Thread(target=lambda: os.system("poetry run python main.py --server --port 8000"),
                     daemon=True).start()

    if not wait_for_zerepy():
        raise Exception("ZerePy server not ready in time!")

    from main_server import create_app  # adjust import as needed
    app = create_app()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

if __name__ == "__main__":
    start_servers()
