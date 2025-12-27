from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="Miravaz Home Lab API",
    description="Control center for home server agents.",
    version="1.0.0"
)

# This model defines what data we expect from the user
class MusicRequest(BaseModel):
    url: str

@app.get("/")
def health_check():
    """Ping this to check if the tunnel is alive."""
    return {"status": "online", "system": "Miravaz Commander"}

@app.post("/rip-song")
def rip_spotify_song(request: MusicRequest):
    """
    Queue a Spotify URL for processing.
    """
    # TODO: In Phase 2, this will spawn a Docker Agent
    print(f"Received request to rip: {request.url}")
    return {"message": "Job queued", "target": request.url}