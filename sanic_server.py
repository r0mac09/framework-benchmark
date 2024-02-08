from sanic import Sanic
from sanic.response import json
from sanic.response import json, raw
import argparse
import asyncio

from utils import read_image, generate_dict

app = Sanic(__name__)

# Synchronous route
@app.route("/test")
def test(request):
    return json({"message": "Hello, World!"})


# Synchronous route
@app.route("/test_load_image")
def test_load_image(request):
    return raw(read_image(request.json["id"]))


@app.route("/test_json")
def test_json(request):
    return json(generate_dict())


@app.route("/kill")
def kill(request):
    request.app.m.terminate()
    return json({"message": "Done ded"})

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--port", type=int)
    
    args = parser.parse_args()
    app.run(host="0.0.0.0", port=args.port, workers=args.workers)
