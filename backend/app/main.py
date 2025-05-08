from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from .routers import dsl
from .config import SVG_OUTPUT_DIR, API_PREFIX
from .database import engine, Base

# Create tables in the database
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="PlanifyDSL API",
    description="API for parsing DSL code and generating floor plans",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins in development
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include routers
app.include_router(dsl.router)

# Mount static files for SVG output if directory exists
if os.path.exists(SVG_OUTPUT_DIR):
    app.mount("/output", StaticFiles(directory=SVG_OUTPUT_DIR), name="output")


@app.get("/")
async def root():
    """Root endpoint to verify the API is running"""
    return {
        "message": "PlanifyDSL API is running",
        "version": "1.0.0",
        "documentation": "/docs"
    }


# Add startup and shutdown events if needed
@app.on_event("startup")
async def startup_event():
    """Initialization tasks on startup"""
    # Ensure output directory exists
    os.makedirs(SVG_OUTPUT_DIR, exist_ok=True)
    print(f"Server started. SVG output directory: {SVG_OUTPUT_DIR}")


if __name__ == "__main__":
    import uvicorn
    from .config import APP_HOST, APP_PORT, DEBUG

    uvicorn.run("app.main:app", host=APP_HOST, port=APP_PORT, reload=DEBUG)