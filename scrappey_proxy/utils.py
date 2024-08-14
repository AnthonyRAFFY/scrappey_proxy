import json
import logging

from requests import Response

logger = logging.getLogger(__name__)


def object_to_dict(_object):
    json_dict = json.loads(json.dumps(_object, default=lambda o: o.__dict__))
    # remove hidden fields
    return {k: v for k, v in json_dict.items() if not k.startswith("__")}


def detect_cloudflare(response: Response):
    cloudflare_keywords = [
        "<title>Just a moment...</title>",
        "<title>Access denied</title>",
        "<title>Attention Required! | Cloudflare</title>",
        "error code: 1020",
        "<title>DDOS-GUARD</title>",
        "cloudflare",
    ]
    response_headers = response.headers
    response_status_code = response.status_code
    response_content = response.text

    if response_status_code == 503 or response_status_code == 403:
        if any(keyword in response_content for keyword in cloudflare_keywords):
            logger.debug(f"Detected Cloudflare by status code: {response_status_code}")
            return True

    if (
        response_headers.get("vary") == "Accept-Encoding,User-Agent"
        and not response_headers.get("content-encoding")
        and "ddos" in response_content
    ):
        logger.debug(f"Detected Cloudflare by headers: {response_headers}")
        return True

    return False
