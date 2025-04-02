import logging
import os

from flask import Flask, request

from scrappey_proxy import utils
from scrappey_proxy.flaresolverr import (
    V1Dispatcher,
    V1RequestBase,
    v1_handler,
)
from scrappey_proxy.handlers import GetRequestHandler, PostRequestHandler

logger = logging.getLogger("gunicorn.error")

PROXY_USERNAME = os.environ.get("PROXY_USERNAME", "")
PROXY_PASSWORD = os.environ.get("PROXY_PASSWORD", "")
PROXY_INTERNAL_IP = os.environ["PROXY_INTERNAL_IP"]
PROXY_EXTERNAL_IP = os.environ["PROXY_EXTERNAL_IP"]
PROXY_INTERNAL_PORT = os.environ["PROXY_INTERNAL_PORT"]
PROXY_EXTERNAL_PORT = os.environ["PROXY_EXTERNAL_PORT"]

proxy = f"http://{PROXY_USERNAME}:{PROXY_PASSWORD}@{PROXY_INTERNAL_IP}:{PROXY_INTERNAL_PORT}"
proxies = {"http": proxy, "https": proxy}
logger.info(f"Configured local proxy: {proxy}")

app = Flask(__name__)

dispatcher = V1Dispatcher(proxies)
dispatcher.register_handler("request.get", GetRequestHandler())
dispatcher.register_handler("request.post", PostRequestHandler())


@app.post("/v1")
def v1_endpoint():
    req = V1RequestBase(request.json)
    res = v1_handler(req, dispatcher)
    return utils.object_to_dict(res)


if __name__ != "__main__":
    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
