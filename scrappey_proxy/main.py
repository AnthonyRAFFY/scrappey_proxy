import logging
import os
from typing import Dict, List

import requests
from flask import Flask, request

from scrappey_proxy import utils
from scrappey_proxy.flaresolverr import (
    STATUS_OK,
    ChallengeResolutionResultT,
    ChallengeResolutionT,
    V1RequestBase,
    V1ResponseBase,
    controller_v1_handler,
)
from scrappey_proxy.scrappey import ScrappeyResponse, get_scrappey

logger = logging.getLogger("gunicorn.error")

PROXY_USERNAME = os.environ.get("PROXY_USERNAME", "")
PROXY_PASSWORD = os.environ.get("PROXY_PASSWORD", "")
PROXY_INTERNAL_IP = os.environ["PROXY_INTERNAL_IP"]
PROXY_EXTERNAL_IP = os.environ["PROXY_EXTERNAL_IP"]
PROXY_INTERNAL_PORT = os.environ["PROXY_INTERNAL_PORT"]
PROXY_EXTERNAL_PORT = os.environ["PROXY_EXTERNAL_PORT"]

saved_cookies = []
saved_headers = {}

proxy = f"http://{PROXY_USERNAME}:{PROXY_PASSWORD}@{PROXY_INTERNAL_IP}:{PROXY_INTERNAL_PORT}"
proxies = {"http": proxy, "https": proxy}
logger.info(f"Using {proxy} as local proxy")

app = Flask(__name__)


def save_cookies(cookies: List[Dict[str, str]]):
    global saved_cookies
    saved_cookies = cookies


def save_user_agent(user_agent: str):
    global saved_headers
    saved_headers["User-Agent"] = user_agent


def get_sendable_cookies():
    sendable_cookies = {}
    for cookie in saved_cookies:
        sendable_cookies[cookie["name"]] = cookie["value"]
    return sendable_cookies


def cmd_request_get(req: V1RequestBase) -> V1ResponseBase:
    challenge_res_result = ChallengeResolutionResultT({})
    challenge_res_result.url = req.url
    challenge_res_result.status = 200

    challenge_res = ChallengeResolutionT({})
    challenge_res.status = STATUS_OK

    if not req.url:
        raise Exception("Request URL should be present")

    logger.info(f"Simple request to {req.url} to check for cloudflare")
    basic_req = requests.get(
        req.url, cookies=get_sendable_cookies(), headers=saved_headers, proxies=proxies
    )

    if utils.detect_cloudflare(basic_req):
        logger.info("Detected Cloudflare")
        scrappey_res: ScrappeyResponse = get_scrappey(req)
        challenge_res_result.cookies = scrappey_res.cookies
        challenge_res.message = "Challenge solved!"
        challenge_res_result.headers = {}
        challenge_res_result.response = scrappey_res.response
        challenge_res_result.userAgent = scrappey_res.user_agent
        save_cookies(scrappey_res.cookies)
        save_user_agent(scrappey_res.user_agent)
    else:
        logger.info("Cloudflare not detected or cf_clearance cookie still valid")
        challenge_res.message = (
            "Cloudflare not detected or cf_clearance cookie still valid!"
        )
        logger.debug(basic_req.text)
        challenge_res_result.headers = {}
        challenge_res_result.cookies = saved_cookies
        challenge_res_result.response = basic_req.text
        challenge_res_result.userAgent = (
            saved_headers["User-Agent"] if "User-Agent" in saved_headers else ""
        )

    challenge_res.result = challenge_res_result

    res = V1ResponseBase({})
    res.status = challenge_res.status
    res.message = challenge_res.message
    res.solution = challenge_res.result
    return res


@app.post("/v1")
def controller_v1_endpoint():
    req = V1RequestBase(request.json)
    res = controller_v1_handler(req, cmd_request_get)

    return utils.object_to_dict(res)


if __name__ != "__main__":
    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
