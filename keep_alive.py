import os
import uvicorn

def keep_alive():
    """Delegates to the FastAPI Gateway which serves the Mini App UI and API endpoints."""
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("gateway.app.main:app", host="0.0.0.0", port=port)

if __name__ == "__main__":
    keep_alive()
