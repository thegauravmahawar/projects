import os
import shutil
from pathlib import Path
import subprocess

def setup_project():
    """Setup the MCP server project"""
    # Create virtual environment
    print("Creating virtual environment...")
    subprocess.run(["python", "-m", "venv", "venv"])

    # Install dependencies
    print("Installing dependencies...")
    if os.name == 'nt':  # Windows
        pip_path = os.path.join("venv", "Scripts", "pip")
    else:  # Unix/Linux/Mac
        pip_path = os.path.join("venv", "bin", "pip")

    subprocess.run([pip_path, "install", "-r", "requirements.txt"])

    # Create .env file from example if it doesn't exist
    if not os.path.exists(".env") and os.path.exists(".env.example"):
        print("Creating .env file from .env.example...")
        shutil.copy(".env.example", ".env")
        print("Don't forget to update the .env file with your API keys!")

    print("Setup complete! You can now start the server with:")
    if os.name == 'nt':  # Windows
        print(r"venv\Scripts\python -m app.main")
    else:  # Unix/Linux/Mac
        print("venv/bin/python -m app.main")

if __name__ == "__main__":
    setup_project()