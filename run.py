import subprocess
import sys
import os
import time
import signal
import logging
from typing import List, Dict

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Process objects to store running servers
processes = []

def start_backend():
    """Start the FastAPI backend server"""
    logger.info("Starting backend server...")
    backend_cmd = ["uvicorn", "backend.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
    backend_process = subprocess.Popen(
        backend_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    processes.append(backend_process)
    logger.info("Backend server started")
    return backend_process

def start_frontend():
    """Start the Streamlit frontend server"""
    logger.info("Starting frontend server...")
    frontend_cmd = ["streamlit", "run", "frontend/pages/main_page.py"]
    frontend_process = subprocess.Popen(
        frontend_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    processes.append(frontend_process)
    logger.info("Frontend server started")
    return frontend_process

def shutdown_servers(sig, frame):
    """Shut down all server processes gracefully"""
    logger.info("Shutting down servers...")
    for process in processes:
        try:
            process.terminate()
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
    logger.info("All servers shut down")
    sys.exit(0)

if __name__ == "__main__":
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, shutdown_servers)
    signal.signal(signal.SIGTERM, shutdown_servers)
    
    try:
        # Ensure the audio directory exists
        os.makedirs("static/audio", exist_ok=True)
        
        # Start servers
        backend_process = start_backend()
        # Wait for backend to start before starting frontend
        time.sleep(3)
        frontend_process = start_frontend()
        
        logger.info("All servers started. Press Ctrl+C to shut down.")
        
        # Monitor servers
        while True:
            backend_returncode = backend_process.poll()
            frontend_returncode = frontend_process.poll()
            
            if backend_returncode is not None:
                logger.error(f"Backend server exited with code {backend_returncode}")
                break
                
            if frontend_returncode is not None:
                logger.error(f"Frontend server exited with code {frontend_returncode}")
                break
                
            time.sleep(1)
            
    except Exception as e:
        logger.error(f"Error running servers: {str(e)}")
    finally:
        shutdown_servers(None, None) 