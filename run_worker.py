import os
import sys

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

# Now we can import from app
from app.workers.unified_worker import worker
import asyncio

if __name__ == "__main__":
    print("Starting unified worker with Python path:", sys.path)
    asyncio.run(worker()) 