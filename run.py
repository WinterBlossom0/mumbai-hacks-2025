#!/usr/bin/env python3
"""
Main runner script for the Misinformation Detection System.
Starts both the FastAPI backend, the Frontend server, and the Reddit Monitor.
"""

import subprocess
import webbrowser
import time
import os
import sys
from pathlib import Path
import threading

# Global stop event for threads
stop_event = threading.Event()
output_threads = []

def print_output(process, name):
    """Print output from a process."""
    try:
        for line in iter(process.stdout.readline, ''):
            if stop_event.is_set():
                break
            if line:
                try:
                    print(f"[{name}] {line.strip()}", flush=True)
                except:
                    pass
    except:
        pass

def start_backend():
    """Start the FastAPI backend server."""
    print("Starting FastAPI backend server...")
    backend_dir = Path(__file__).parent / "backend"
    
    # Start uvicorn
    backend_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
        cwd=backend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    # Start thread to print backend output
    thread = threading.Thread(target=print_output, args=(backend_process, "BACKEND"))
    thread.start()
    output_threads.append(thread)
    
    return backend_process

def start_frontend():
    """Start a simple HTTP server for the frontend."""
    print("Starting frontend server...")
    frontend_dir = Path(__file__).parent / "frontend"
    
    # Start Next.js dev server
    npm_cmd = "npm.cmd" if os.name == "nt" else "npm"
    
    frontend_process = subprocess.Popen(
        [npm_cmd, "run", "dev"],
        cwd=frontend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    # Start thread to print frontend output
    thread = threading.Thread(target=print_output, args=(frontend_process, "FRONTEND"))
    thread.start()
    output_threads.append(thread)
    
    return frontend_process

def start_reddit_monitor():
    """Start the Reddit monitor script."""
    print("Starting Reddit monitor...")
    backend_dir = Path(__file__).parent / "backend"
    monitor_script = backend_dir / "reddit" / "monitor.py"
    
    if not monitor_script.exists():
        print(f"⚠ Reddit monitor script not found at {monitor_script}")
        return None

    # Start monitor
    monitor_process = subprocess.Popen(
        [sys.executable, "-u", "reddit/monitor.py"],
        cwd=backend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    # Start thread to print monitor output
    thread = threading.Thread(target=print_output, args=(monitor_process, "REDDIT"))
    thread.start()
    output_threads.append(thread)
    
    return monitor_process

def wait_for_server(url, timeout=30):
    """Wait for a server to be ready."""
    import urllib.request
    import urllib.error
    
    import socket
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            urllib.request.urlopen(url, timeout=2)
            return True
        except (urllib.error.URLError, ConnectionRefusedError, TimeoutError, socket.timeout):
            time.sleep(0.5)
    return False

def open_browser():
    """Open the frontend in the default browser."""
    print("\nWaiting for servers to be ready...")
    
    # Wait for backend
    if wait_for_server("http://localhost:8000/api/health"):
        print("✓ Backend is ready")
    else:
        print("⚠ Backend might not be ready yet")
    
    # Wait for frontend
    if wait_for_server("http://localhost:3000"):
        print("✓ Frontend is ready")
    else:
        print("⚠ Frontend might not be ready yet")
    
    print("\nOpening browser...")
    time.sleep(1)
    webbrowser.open("http://localhost:3000")

def main():
    print("="*70)
    print("Truth Lens - Misinformation Detection System")
    print("="*70)
    print()
    
    backend_process = None
    frontend_process = None
    monitor_process = None
    
    try:
        # Start backend
        backend_process = start_backend()
        print("✓ Backend starting on http://localhost:8000")
        
        # Start frontend
        frontend_process = start_frontend()
        print("✓ Frontend starting on http://localhost:3000")
        
        # Start Reddit monitor
        monitor_process = start_reddit_monitor()
        if monitor_process:
            print("✓ Reddit monitor starting")
        
        # Open browser
        open_browser()
        print("✓ Browser opened")
        
        print()
        print("="*70)
        print("System is running!")
        print("="*70)
        print("Backend API: http://localhost:8000")
        print("Frontend: http://localhost:3000")
        print("Reddit Monitor: Running")
        print()
        print("Press Ctrl+C to stop all servers")
        print("="*70)
        print()
        
        # Keep the script running
        while True:
            time.sleep(1)
            # Check if processes are still running
            if backend_process.poll() is not None:
                print("\n✗ Backend process stopped unexpectedly")
                break
            if frontend_process.poll() is not None:
                print("\n✗ Frontend process stopped unexpectedly")
                break
            if monitor_process and monitor_process.poll() is not None:
                print("\n⚠ Reddit monitor process stopped unexpectedly")
                # Don't break, just log
        
    except KeyboardInterrupt:
        print("\n\nStopping servers...")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Signal threads to stop
        stop_event.set()
        
        # Terminate processes
        if backend_process:
            backend_process.terminate()
        if frontend_process:
            frontend_process.terminate()
        if monitor_process:
            monitor_process.terminate()
        
        # Wait for threads to finish (with timeout)
        for thread in output_threads:
            thread.join(timeout=2)
        
        print("✓ All servers stopped")

if __name__ == "__main__":
    main()
