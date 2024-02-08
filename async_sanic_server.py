from sanic import Sanic
from sanic.response import json
from sanic.response import json, raw
import argparse

from utils import read_image, generate_dict

app = Sanic(__name__)

# Asynchronous route
@app.route("/test")
async def async_test(request):
    return json({"message": "Async Hello, World!"})


# Asynchronous route
@app.route("/test_load_image")
async def async_test_load_image(request):
    return raw(read_image(request.json["id"]))


@app.route("/test_json")
async def async_test_json(request):
    return json(generate_dict())


@app.route("/kill")
async def async_kill(request):
    request.app.m.terminate()
    return json({"message": "Done ded"})


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--port", type=int)
    
    args = parser.parse_args()
    app.run(host="0.0.0.0", port=args.port, workers=args.workers)


