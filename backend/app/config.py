import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '.env')
load_dotenv(dotenv_path=env_path)

# API configuration
API_PREFIX = "/api"
APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", "5001"))
DEBUG = os.getenv("DEBUG", "True").lower() == "true"

# Output configuration
SVG_OUTPUT_DIR = os.getenv("SVG_OUTPUT_DIR", os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "output"))

# Create output directory if it doesn't exist
os.makedirs(SVG_OUTPUT_DIR, exist_ok=True)