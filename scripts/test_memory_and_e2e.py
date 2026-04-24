import os
import psutil
import time
import requests
import urllib.request

API_URL = "http://127.0.0.1:8000"

def get_process_memory():
    # Find the uvicorn process
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['cmdline'] and 'app.main' in ' '.join(proc.info['cmdline']):
                return proc.memory_info().rss / 1024 / 1024 # MB
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return 0

def download_sample_audio():
    os.makedirs("tmp-tests", exist_ok=True)
    if not os.path.exists("tmp-tests/horse.ogg"):
        urllib.request.urlretrieve("https://www.w3schools.com/html/horse.ogg", "tmp-tests/horse.ogg")
    return "tmp-tests/horse.ogg"

def test_health():
    res = requests.get(f"{API_URL}/health")
    print(f"Health Check: {res.status_code} - {res.json()}")
    return res.status_code == 200

def test_transcribe(filepath):
    start = time.time()
    with open(filepath, 'rb') as f:
        files = {'file': (os.path.basename(filepath), f, 'audio/ogg')}
        res = requests.post(f"{API_URL}/transcribe", files=files)
    end = time.time()
    print(f"Transcribe {filepath}: {res.status_code} in {end-start:.2f}s")
    if res.status_code == 200:
        print(f"Text preview: {res.json().get('text', '')[:100]}")
    return res.status_code == 200

if __name__ == "__main__":
    print(f"Initial Memory: {get_process_memory():.2f} MB")
    
    if test_health():
        print(f"Memory after health: {get_process_memory():.2f} MB")
        
        sample = download_sample_audio()
        
        for i in range(3):
            print(f"\n--- Request {i+1} ---")
            test_transcribe(sample)
            print(f"Memory after request {i+1}: {get_process_memory():.2f} MB")
            
        # Verify tmp directory
        tmp_files = os.listdir('/tmp')
        whisper_tmps = [f for f in tmp_files if f.startswith('tmp')]
        print(f"\nTmp files in /tmp: {len(whisper_tmps)} found. (Cleanup check)")
