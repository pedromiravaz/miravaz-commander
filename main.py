from fastapi import FastAPI
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
def rip_spotify_song(request: MusicRequest):
    print(f"Received request to rip: {request.url}")
    return {"message": "Job queued", "target": request.url}