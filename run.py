import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

# Import backend application
import uvicorn
from backend.app.config import APP_HOST, APP_PORT, DEBUG

if __name__ == "__main__":
    print(f"Starting server on {APP_HOST}:{APP_PORT}")
    uvicorn.run("backend.app.main:app", host=APP_HOST, port=APP_PORT, reload=DEBUG)