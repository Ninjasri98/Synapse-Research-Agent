from fastapi import FastAPI, status, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from datetime import datetime
from contextlib import asynccontextmanager

from services import initialize_db_pool, close_db_pool
from routers.research import router as research_router
from routers.chat import router as chat_router

# Create router for API endpoints
router = APIRouter(prefix="/api")

@router.get("/health", summary="API Health Check")
async def health_check():
    logger.debug("Health check requested")
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Define lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    logger.info("API server started")

    # Initialize database connection pool
    logger.info("Initializing database connection pool")
    await initialize_db_pool()

    yield

    # Shutdown logic
    # Close database connection pool
    logger.info("Closing database connection pool")
    await close_db_pool()

    logger.info("API server shutting down")

# Create FastAPI app with lifespan
app = FastAPI(
    title="Synapse Research Agent",
    description="API for running intelligent research agents in the background",
    version="0.1.0",
    lifespan=lifespan,
)

# Add CORS middleware (adjust origins for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Example: ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the routers
app.include_router(router)
app.include_router(research_router, prefix="/api")
app.include_router(chat_router, prefix="/api")