#!/usr/bin/env python3
"""
Launcher script for Certificate Generator GUI
"""

import subprocess
import sys
import os

def main():
    """Launch the Streamlit GUI application."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    gui_script = os.path.join(script_dir, "certificate_gui.py")

    if not os.path.exists(gui_script):
        print(f"Error: GUI script not found at {gui_script}")
        sys.exit(1)

    print("Starting Certificate Generator GUI...")
    print(f"Script location: {gui_script}")

    try:
        # Run streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", gui_script,
            "--server.port", "8501",
            "--server.address", "localhost",
            "--theme.base", "light"
        ], cwd=script_dir)
    except KeyboardInterrupt:
        print("\nGUI application stopped.")
    except Exception as e:
        print(f"Error running GUI: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
