from pathlib import Path
import requests
import time
import subprocess
import concurrent.futures
import numpy as np
from PIL import Image
import string
import random
from tqdm import tqdm

BASIC_REQUESTS = 10000
IMAGE_REQUESTS = 10000
JSON_REQUESTS = 10000
COMMANDS = [
    ["./venv/Scripts/python.exe", "sanic_server.py"],
    ["./venv/Scripts/python.exe", "async_sanic_server.py"],
    ["./venv/Scripts/python.exe", "sanic_server.py", "--workers", "8"],
    ["./venv/Scripts/python.exe", "async_sanic_server.py", "--workers", "8"],
    ["./venv/Scripts/python.exe", "tornado_server.py"],
    ["./venv/Scripts/python.exe", "tornado_server.py", "--run_async"],
]


def get_image(port, img):
    start = time.monotonic()
    requests.get(f"http://127.0.0.1:{port}/test_load_image", json={"id": img})
    return time.monotonic() - start


def basic_request(port):
    start = time.monotonic()
    requests.get(f"http://127.0.0.1:{port}/test")
    return time.monotonic() - start


def get_json(port):
    start = time.monotonic()
    requests.get(f"http://127.0.0.1:{port}/test_json")
    return time.monotonic() - start


PORT = 44000

if __name__ == "__main__":
    images_path = Path("./test_images")
    images_path.mkdir(exist_ok=True)
    
    images = [str(p.resolve()) for p in images_path.glob('*.jpg')]
    if len(images) < IMAGE_REQUESTS:
        print("Generating images ...")
        rng = np.random.default_rng(69420)
        for i in tqdm(range(len(images), IMAGE_REQUESTS)):
            img_id = images_path / ''.join(random.choices(string.ascii_letters, k=20)) + '.jpg'
            Image.fromarray((rng.random((720, 1280, 3))*255).astype(np.uint8)).save(images_path / img_id)
            images.append(str(img_id.resolve()))
    else:
        images = images[:IMAGE_REQUESTS]

    for port, cmd in enumerate(COMMANDS, start=PORT):
        cmd += ["--port", str(port)]
        with open(f"server_logs/{port}_{cmd[1].split('.')[0]}.log", "w") as log:
            try:
                server_process = subprocess.Popen(cmd, 
                                                  stdout=log,
                                                  stderr=log)
                print(f"Giving the server time to start: CMD {' '.join(cmd)}")
                for _ in tqdm(range(100)): time.sleep(0.1)
                with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
                    futures = [executor.submit(basic_request, port) for _ in range(BASIC_REQUESTS)]
                    start = time.monotonic()
                    concurrent.futures.wait(futures)
                    duration = time.monotonic() - start
                    avg_resp_time = 1000 * sum([f.result() for f in futures]) / len(futures)
                    print(f"BASIC RPS: {BASIC_REQUESTS/duration:.3f}, TTC: {duration:.3f}s, ART: {avg_resp_time:.1f}ms")

                    futures = [executor.submit(get_image, port, img_id) for img_id in images]
                    start = time.monotonic()
                    concurrent.futures.wait(futures)
                    duration = time.monotonic() - start
                    avg_resp_time = 1000* sum([f.result() for f in futures]) / len(futures)
                    print(f"IMAGE RPS: {IMAGE_REQUESTS/duration:.3f}, TTC: {duration:.3f}s, ART: {avg_resp_time:.1f}ms")
                    
                    futures = [executor.submit(get_json, port) for _ in range(JSON_REQUESTS)]
                    start = time.monotonic()
                    concurrent.futures.wait(futures)
                    duration = time.monotonic() - start
                    avg_resp_time = 1000* sum([f.result() for f in futures]) / len(futures)
                    print(f"JSON RPS: {JSON_REQUESTS/duration:.3f}, TTC: {duration:.3f}s, ART: {avg_resp_time:.1f}ms")

                requests.get(f"http://127.0.0.1:{port}/kill")
            except Exception as e:
                print(cmd, str(e))
                server_process.terminate()
                server_process.wait()
                break
            finally:
                server_process.terminate()
                server_process.wait()
            time.sleep(1)
