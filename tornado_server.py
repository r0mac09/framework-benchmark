import asyncio
import tornado.ioloop
import tornado.web
import tornado.gen
import json
import argparse

from utils import read_image, generate_dict

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(json.dumps({"message": "Hello, World!"}))


class TestLoadImageHandler(tornado.web.RequestHandler):
    def get(self):
        try:
            img_id = json.loads(self.request.body.decode("utf-8"))["id"]
            self.set_header("Content-Type", "image/jpeg")
            self.write(read_image(img_id))
        except Exception as e:
            raise tornado.web.HTTPError(404, reason=f"Error processing image: {str(e)}")


class TestJsonHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(generate_dict())


def get_app(port):
    app = tornado.web.Application([
        (r"/test", MainHandler),
        (r"/test_load_image", TestLoadImageHandler),
        (r"/test_json", TestJsonHandler)
    ])
    
    app.listen(port, reuse_port=True)
    
    return app

async def run_async(port):
    app = get_app(port)
    await asyncio.Event().wait()


def run(port):
    app = get_app(port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run_async", action="store_true")
    parser.add_argument("--port", type=int)

    args = parser.parse_args()
    if args.run_async:
        asyncio.run(run_async(args.port))
    else:
        run(args.port)