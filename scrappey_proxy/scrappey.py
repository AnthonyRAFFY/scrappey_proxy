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
logger.info(f"Using {proxy_url} as scrappey's proxy")


@dataclass
class ScrappeyResponse:
    response: str
    status_code: int
    cookies: List[Dict[str, str]]
    user_agent: str


scrappey = Scrappey(os.environ["SCRAPPEY_API_KEY"])


# Function which takes a request and forwards it to scrappey
def get_scrappey(request: V1RequestBase):
    logger.info(f"Calling scrappey for URL : {request.url}")

    get_request_result = scrappey.get({"url": request.url, "proxy": proxy_url})

    if (
        "solution" in get_request_result
        and "response" in get_request_result["solution"]
    ):
        return ScrappeyResponse(
            get_request_result["solution"]["response"],
            200,
            get_request_result["solution"]["cookies"],
            get_request_result["solution"]["userAgent"],
        )
    else:
        return ScrappeyResponse("", 500, [], "")
