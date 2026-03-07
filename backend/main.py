from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings
from backend.api.routes import router

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="ForestEye: AI-Driven Forest Monitoring & Analytics API for Dang District, Gujarat"
)

# CORS middleware - allows frontend to connect
# Must be added BEFORE routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "ForestEye API",
        "version": settings.VERSION,
        "docs": "/docs",
        "endpoints": {
            "health": f"{settings.API_V1_PREFIX}/health",
            "dates": f"{settings.API_V1_PREFIX}/dates",
            "boundary": f"{settings.API_V1_PREFIX}/boundary",
            "analyze": f"{settings.API_V1_PREFIX}/analyze"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
