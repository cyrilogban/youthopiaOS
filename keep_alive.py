import threading
import uvicorn
from fastapi import FastAPI
import os

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "Theo is alive and running!"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

def run_server():
    # Render assigns a port via the PORT environment variable
    port = int(os.environ.get("PORT", 8080))
    # Bind to 0.0.0.0 to expose it to the outside world
    uvicorn.run(app, host="0.0.0.0", port=port)

def keep_alive():
    """Starts a background web server to trick Render into thinking this is a Web Service."""
    server_thread = threading.Thread(target=run_server)
    # Daemon thread ensures it closes when the main bot process stops
    server_thread.daemon = True
    server_thread.start()
