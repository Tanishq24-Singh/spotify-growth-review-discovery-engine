import sys
import os

# Add parent directory to sys.path so we can import modules from the project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from server import app
from workflow_pipeline import init_db
from server import init_server_db

# Initialize database schemas only when running locally (not on Vercel serverless)
# to prevent sqlite3.OperationalError on Vercel's read-only filesystem.
if not os.getenv("VERCEL"):
    try:
        init_db()
        init_server_db()
    except Exception as e:
        print(f"[Vercel Startup] Database initialization skipped: {e}")
