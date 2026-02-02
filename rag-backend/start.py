import uvicorn
import os
import sys

# Add the current directory to sys.path to ensure module resolution works
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    # Use 0.0.0.0 to be accessible from all interfaces
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
