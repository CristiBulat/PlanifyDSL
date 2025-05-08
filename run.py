import sys
import os

# Add the project root to the path to ensure imports work correctly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the FastAPI app
import uvicorn
from app.config import APP_HOST, APP_PORT, DEBUG

if __name__ == "__main__":
    uvicorn.run("app.main:app", host=APP_HOST, port=APP_PORT, reload=DEBUG)