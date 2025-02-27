import os
import time
import subprocess

EXTRACT_SCRIPT = "extract_confluence.py"
NORMALIZE_SCRIPT = "normalize_data.py"
VECTORIZING_SCRIPT = "vectorize_data.py"
API_SCRIPT = "api.py"
STREAMLIT_SCRIPT = "chatbot_ui.py"

def run_script(script_name):
    """Executes a Python script and waits for it to complete."""
    print(f"🔄 Running {script_name}...")
    result = subprocess.run(["python", script_name], capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ {script_name} completed successfully.")
    else:
        print(f"❌ Error in {script_name}:\n{result.stderr}")

def restart_fastapi():
    """Restarts the FastAPI server."""
    print("🔄 Restarting FastAPI server...")
    subprocess.run(["pkill", "-f", API_SCRIPT])
    subprocess.Popen(["python", API_SCRIPT])
    print("✅ FastAPI restarted.")

def main():
    """Executes the full data update pipeline."""
    print("\n🚀 Starting full pipeline update...")

    run_script(EXTRACT_SCRIPT)
    run_script(NORMALIZE_SCRIPT)
    run_script(VECTORIZING_SCRIPT)
    restart_fastapi()

    print("✅ Update complete! Changes are now reflected in the chatbot.")

if __name__ == "__main__":
    main()
