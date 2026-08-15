"""YouThopiaOS gateway — the server-side trust boundary for the Mini App.

For now it only exposes a health check so we can confirm the server runs.
Telegram initData validation arrives in later steps.
"""
from fastapi import FastAPI

app = FastAPI(title="YouThopiaOS Gateway")


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness probe — proves the server is up and responding."""
    return {"status": "ok"}
