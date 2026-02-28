import os
import subprocess
import time
import requests

def main():
    # 1. Start the API in a background process
    print("Starting FastAPI Backend...")
    # On Windows, we might need shell=True for uvicorn depending on how it's installed,
    # but providing uvicorn directly usually works if it's in PATH.
    # Alternatively we can use sys.executable -m uvicorn
    import sys
    api_process = subprocess.Popen([sys.executable, "-m", "uvicorn", "unihelp.api.main:app", "--host", "0.0.0.0", "--port", "8000"])
    
    # 2. Wait a moment for API to initialize
    print("Waiting for API to initialize...")
    time.sleep(5) # give it a bit more time to spin up
    
    try:
        res = requests.get("http://127.0.0.1:8000/")
        if res.status_code == 200:
            print("API is up and running!")
        else:
            print(f"API returned status {res.status_code}")
    except requests.exceptions.ConnectionError:
        print("Warning: API doesn't seem to be responding on port 8000")
        
    print("\nStarting Streamlit UI...")
    # 3. Use subprocess to run streamlit
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "unihelp/ui/app.py", "--server.port", "8501", "--server.address", "0.0.0.0", "--browser.gatherUsageStats", "false"])
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        api_process.terminate()

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    main()
