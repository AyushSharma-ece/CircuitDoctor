"""
CircuitDoctor - Master FastAPI Application Entrypoint
AI-Powered PCB Defect Detection and Inspection Platform Backend
Preloads YOLO model once at application startup and shares it across requests.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.core.config import settings
from backend.app.database.session import engine, Base
from backend.app.api.endpoints import health, model, inspections, stats, images, dataset

# Ensure database tables are created on startup
Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager: preloads YOLO detection model on startup."""
    print("[Lifespan] Initializing CircuitDoctor services...")
    try:
        from backend.app.services.detection_service import DetectionService
        detector = DetectionService.get_instance()
        if detector.load_model():
            print(f"[Lifespan] Successfully preloaded YOLO model from: {detector.model_path}")
        else:
            print("[Lifespan] Model weights not found yet; will load dynamically once available.")
    except Exception as e:
        print(f"[Lifespan] Warning during model initialization: {e}")

    yield

    print("[Lifespan] Shutting down CircuitDoctor backend.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="Automated AI-powered visual defect inspection platform for printed circuit boards.",
    lifespan=lifespan,
)

# Configure Cross-Origin Resource Sharing (CORS) for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers under configured prefix
app.include_router(health.router, prefix=settings.API_V1_PREFIX, tags=["Health"])
app.include_router(model.router, prefix=settings.API_V1_PREFIX, tags=["Model"])
app.include_router(dataset.router, prefix=settings.API_V1_PREFIX, tags=["Dataset"])
app.include_router(inspections.router, prefix=settings.API_V1_PREFIX, tags=["Inspections"])
app.include_router(stats.router, prefix=settings.API_V1_PREFIX, tags=["Statistics"])
app.include_router(images.router, prefix=settings.API_V1_PREFIX, tags=["Images"])


@app.get("/")
def root():
    """Root metadata endpoint."""
    return {
        "project": settings.PROJECT_NAME,
        "tagline": "AI-Powered PCB Defect Detection and Inspection",
        "version": settings.PROJECT_VERSION,
        "documentation": "/docs",
        "api_v1": settings.API_V1_PREFIX,
        "limitation_notice": (
            "CircuitDoctor performs visual defect detection and surface analysis. "
            "Optical AI does not confirm electrical continuity, internal layer faults, "
            "or component values. Electrical verification is recommended."
        )
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.app.main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=True
    )
