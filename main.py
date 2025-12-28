from fastapi import FastAPI, HTTPException
import httpx
from pydantic import BaseModel
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource

# --- OBSERVABILITY SETUP ---
# 1. Name the service so it shows up correctly in Jaeger
resource = Resource.create({"service.name": "miravaz-commander"})

# 2. Configure the provider
trace.set_tracer_provider(TracerProvider(resource=resource))

# 3. Connect to the Jaeger Container (Port 4317 is the data pipe)
# Note: 'jaeger' is the container name in docker-compose
otlp_exporter = OTLPSpanExporter(endpoint="http://jaeger:4317", insecure=True)

# 4. Tell the app to send data in batches (better performance)
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(otlp_exporter))

# --- APP DEFINITION ---
app = FastAPI(
    title="Miravaz Home Lab API",
    description="Control center for home server agents.",
    version="1.1.0"
)

# 5. Turn on the magic auto-instrumentation
FastAPIInstrumentor.instrument_app(app)

class MusicRequest(BaseModel):
    url: str

@app.get("/")
def health_check():
    """Ping this to check if the tunnel is alive."""
    # This function will now generate a trace!
    return {"status": "online", "system": "Miravaz Commander", "observability": "active"}

@app.post("/rip-song")
async def rip_spotify_song(request: MusicRequest):
    print(f"Received request to rip: {request.url}")
    
    worker_url = "http://spotify2mp3:8000/v1/convert"
    
    async with httpx.AsyncClient() as client:
        try:
            # Forward the request to the worker
            # The worker expects {"url": "..."} which matches our MusicRequest model
            resp = await client.post(
                worker_url, 
                json={"url": request.url}, 
                timeout=120.0 # Allow 2 minutes for download/processing
            )
            
            # Check for errors
            if resp.status_code != 200:
                print(f"Worker failed: {resp.text}")
                raise HTTPException(status_code=resp.status_code, detail=f"Worker error: {resp.text}")
            
            # Return the worker's response (metadata + base64 content) directly
            return resp.json()
            
        except httpx.RequestError as exc:
            print(f"An error occurred while requesting {exc.request.url!r}.")
            raise HTTPException(status_code=503, detail=f"Worker unreachable: {exc}")