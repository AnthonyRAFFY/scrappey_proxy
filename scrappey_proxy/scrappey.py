import logging
import os
from dataclasses import dataclass
from typing import Dict, List

from scrappeycom.scrappey import Scrappey

from scrappey_proxy.flaresolverr import V1RequestBase

logger = logging.getLogger("gunicorn.error")

PROXY_USERNAME = os.environ.get("PROXY_USERNAME", "")
PROXY_PASSWORD = os.environ.get("PROXY_PASSWORD", "")
PROXY_EXTERNAL_IP = os.environ["PROXY_EXTERNAL_IP"]
PROXY_EXTERNAL_PORT = os.environ["PROXY_EXTERNAL_PORT"]

proxy_url = f"http://{PROXY_USERNAME}:{PROXY_PASSWORD}@{PROXY_EXTERNAL_IP}:{PROXY_EXTERNAL_PORT}"
logger.info(f"Configured public proxy (Used by scrappey.com): {proxy_url}")


@dataclass
class ScrappeyResponse:
    response: str
    status_code: int
    cookies: List[Dict[str, str]]
    user_agent: str


scrappey = Scrappey(os.environ["SCRAPPEY_API_KEY"])


def get_scrappey(request: V1RequestBase):
    """Takes a get request and forward it to scrappey"""
    logger.info(f"Forwarding GET request to Scrappey API: URL={request.url}")

    request_result = scrappey.get({"url": request.url, "proxy": proxy_url})

    success = "solution" in request_result and "response" in request_result["solution"]
    logger.info(f"Received response from Scrappey: Status={200 if success else 500}")

    if success:
        return ScrappeyResponse(
            request_result["solution"]["response"],
            200,
            request_result["solution"]["cookies"],
            request_result["solution"]["userAgent"],
        )
    else:
        return ScrappeyResponse("", 500, [], "")


def post_scrappey(request: V1RequestBase):
    """Takes a post request and forward it to scrappey"""
    logger.info(f"Forwarding POST request to Scrappey API: URL={request.url}")

    request_result = scrappey.post(
        {"url": request.url, "postData": request.postData, "proxy": proxy_url}
    )

    success = "solution" in request_result and "response" in request_result["solution"]
    logger.info(f"Received response from Scrappey: Status={200 if success else 500}")

    if success:
        return ScrappeyResponse(
            request_result["solution"]["response"],
            200,
            request_result["solution"]["cookies"],
            request_result["solution"]["userAgent"],
        )
    else:
        return ScrappeyResponse("", 500, [], "")
