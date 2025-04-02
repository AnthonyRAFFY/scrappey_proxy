import json
import logging

from requests import Response

logger = logging.getLogger(__name__)

CLOUDFLARE_KEYWORDS = [
    "<title>Just a moment...</title>",
    "<title>Access denied</title>",
    "<title>Attention Required! | Cloudflare</title>",
    "error code: 1020",
    "<title>DDOS-GUARD</title>",
    "cloudflare",
    "cdn-cgi/challenge-platform",
]

CLOUDFLARE_SELECTORS = [
    # Cloudflare
    "#cf-challenge-running",
    ".ray_id",
    ".attack-box",
    "#cf-please-wait",
    "#challenge-spinner",
    "#trk_jschal_js",
    "#turnstile-wrapper",
    ".lds-ring",
    # Custom CloudFlare for EbookParadijs, Film-Paleis, MuziekFabriek and Puur-Hollands
    "td.info #js_info",
    # Fairlane / pararius.com
    "div.vc div.text-box h2",
]


def object_to_dict(_object):
    json_dict = json.loads(json.dumps(_object, default=lambda o: o.__dict__))
    # remove hidden fields
    return {k: v for k, v in json_dict.items() if not k.startswith("__")}


def detect_cloudflare(response: Response):
    response_headers = response.headers
    response_status_code = response.status_code
    response_content = response.text

    if response_status_code == 503 or response_status_code == 403:
        if any(keyword in response_content for keyword in CLOUDFLARE_KEYWORDS):
            logger.debug(
                f"Cloudflare detection: Matched by status code {response_status_code} | Keywords found in response content"
            )
            return True

    if any(keyword in response_content for keyword in CLOUDFLARE_SELECTORS):
        logger.debug(
            "Cloudflare detection: Matched by selectors | selectors found in response content"
        )
        return True
    if (
        response_headers.get("vary") == "Accept-Encoding,User-Agent"
        and not response_headers.get("content-encoding")
        and "ddos" in response_content
    ):
        logger.debug(f"Detected Cloudflare by headers: {response_headers}")
        return True

    return False
