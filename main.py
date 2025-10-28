from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import transcript, icebreaker
from app.workers.unified_worker import worker
import asyncio
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🔁 Starting unified worker on FastAPI startup...")
    asyncio.create_task(worker())
    yield
    # Shutdown (if needed)
    print("👋 Shutting down...")

app = FastAPI(
    title="MyBizSherpa Backend",
    description="AI-powered backend for transcript and outreach features",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://my-biz-sherpa-frontend.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(transcript.router, prefix="/api", tags=["Transcript"])
app.include_router(icebreaker.router, prefix="/api", tags=["Icebreaker"])
