#!/usr/bin/env python3
"""
Runner script for the Web Extension Backend.
Starts only the extension backend on port 8001.
"""

import subprocess
import sys
from pathlib import Path


def main():
    print("="*70)
    print("Truth Lens - Web Extension Backend")
    print("="*70)
    print()
    
    extension_backend_dir = Path(__file__).parent #/ "extension-backend"
    
    if not extension_backend_dir.exists():
        print("✗ Error: extension-backend directory not found!")
        print(f"  Expected location: {extension_backend_dir}")
        return 1
    
    print("Starting Web Extension Backend on http://localhost:8001...")
    print()
    
    try:
        # Start uvicorn
        subprocess.run(
            [sys.executable, "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8001", "--reload"],
            cwd=extension_backend_dir,
            check=True
        )
    except KeyboardInterrupt:
        print("\n\nStopping extension backend...")
        print("✓ Extension backend stopped")
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Error running extension backend: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
