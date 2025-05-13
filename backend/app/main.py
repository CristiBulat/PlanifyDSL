# Add DSL module to Python path
import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)
print(f"Added {project_root} to Python path")

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .routers import dsl
from .config import SVG_OUTPUT_DIR, API_PREFIX
from .database import Base, engine

# Create database tables
try:
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")
except Exception as e:
    print(f"Warning: Could not create database tables: {e}")

# Initialize FastAPI app
app = FastAPI(
    title="PlanifyDSL API",
    description="API for parsing DSL code and generating floor plans",
    version="1.0.0",
)

# Add middleware for SVG CORS headers
@app.middleware("http")
async def add_cors_headers_for_svg(request: Request, call_next):
    response = await call_next(request)
    if request.url.path.endswith('.svg') or '.svg?' in request.url.path:
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

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

# Mount static files for SVG output
if os.path.exists(SVG_OUTPUT_DIR):
    app.mount("/output", StaticFiles(directory=SVG_OUTPUT_DIR), name="output")
    print(f"Mounted static files from {SVG_OUTPUT_DIR}")
else:
    print(f"Warning: Output directory {SVG_OUTPUT_DIR} does not exist")


@app.get("/")
async def root():
    """Root endpoint to verify the API is running"""
    return {
        "message": "PlanifyDSL API is running",
        "version": "1.0.0",
        "documentation": "/docs"
    }


# Add startup event
@app.on_event("startup")
async def startup_event():
    """Initialization tasks on startup"""
    # Ensure output directory exists
    os.makedirs(SVG_OUTPUT_DIR, exist_ok=True)
    print(f"Server started. SVG output directory: {SVG_OUTPUT_DIR}")