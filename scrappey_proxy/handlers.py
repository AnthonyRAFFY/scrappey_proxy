import logging
from typing import Dict

import requests

from scrappey_proxy import utils
from scrappey_proxy.flaresolverr import (
    STATUS_OK,
    ChallengeResolutionResultT,
    ChallengeResolutionT,
    V1Handler,
    V1RequestBase,
    V1ResponseBase,
)
from scrappey_proxy.scrappey import ScrappeyResponse, get_scrappey, post_scrappey
from scrappey_proxy.session import (
    get_sendable_cookies,
    get_session_cookies,
    get_session_headers,
    save_cookies,
    save_user_agent,
)

logger = logging.getLogger("gunicorn.error")


class GetRequestHandler(V1Handler):
    def handle(self, req: V1RequestBase, proxies: Dict[str, str]) -> V1ResponseBase:  # noqa: F821
        challenge_res_result = ChallengeResolutionResultT({})
        challenge_res_result.url = req.url
        challenge_res_result.status = 200

        challenge_res = ChallengeResolutionT({})
        challenge_res.status = STATUS_OK

        if not req.url:
            raise Exception("Request URL should be present")

        logger.info(
            f"Making initial request to {req.url} to detect Cloudflare protection"
        )
        basic_req = requests.get(
            req.url,
            cookies=get_sendable_cookies(),
            headers=get_session_headers(),
            proxies=proxies,
        )

        if utils.detect_cloudflare(basic_req):
            logger.info(
                f"Cloudflare protection detected on {req.url} - forwarding the request to Scrappey.com"
            )
            scrappey_res: ScrappeyResponse = get_scrappey(req)
            challenge_res_result.cookies = scrappey_res.cookies
            challenge_res.message = "Challenge solved!"
            challenge_res_result.headers = {}
            challenge_res_result.response = scrappey_res.response
            challenge_res_result.userAgent = scrappey_res.user_agent
            save_cookies(scrappey_res.cookies)
            save_user_agent(scrappey_res.user_agent)
        else:
            logger.info(
                f"No Cloudflare protection detected or existing cf_clearance cookie valid for {req.url}"
            )
            challenge_res.message = "No Cloudflare protection detected or existing cf_clearance cookie valid"
            logger.debug(basic_req.text)
            challenge_res_result.headers = {}
            challenge_res_result.cookies = get_session_cookies()
            challenge_res_result.response = basic_req.text
            challenge_res_result.userAgent = (
                get_session_headers()["User-Agent"]
                if "User-Agent" in get_session_headers()
                else ""
            )

        challenge_res.result = challenge_res_result

        res = V1ResponseBase({})
        res.status = challenge_res.status
        res.message = challenge_res.message
        res.solution = challenge_res.result
        return res


class PostRequestHandler(V1Handler):
    def handle(self, req: V1RequestBase, proxies: Dict[str, str]) -> V1ResponseBase:
        challenge_res_result = ChallengeResolutionResultT({})
        challenge_res_result.url = req.url
        challenge_res_result.status = 200

        challenge_res = ChallengeResolutionT({})
        challenge_res.status = STATUS_OK

        if not req.url:
            raise Exception("Request URL should be present")
        if req.postData is None:
            raise Exception(
                "Request parameter 'postData' is mandatory in 'request.post' command."
            )

        logger.info(
            f"Making initial request to {req.url} to detect Cloudflare protection"
        )
        basic_req = requests.get(
            req.url,
            cookies=get_sendable_cookies(),
            headers=get_session_headers(),
            proxies=proxies,
        )

        if utils.detect_cloudflare(basic_req):
            logger.info(
                f"Cloudflare protection detected on {req.url} - forwarding the request to Scrappey.com"
            )
            scrappey_res: ScrappeyResponse = post_scrappey(req)
            challenge_res_result.cookies = scrappey_res.cookies
            challenge_res.message = "Challenge solved!"
            challenge_res_result.headers = {}
            challenge_res_result.response = scrappey_res.response
            challenge_res_result.userAgent = scrappey_res.user_agent
            save_cookies(scrappey_res.cookies)
            save_user_agent(scrappey_res.user_agent)
        else:
            logger.info(
                f"No Cloudflare protection detected or existing cf_clearance cookie valid for {req.url}"
            )
            challenge_res.message = "No Cloudflare protection detected or existing cf_clearance cookie valid"
            logger.debug(basic_req.text)
            challenge_res_result.headers = {}
            challenge_res_result.cookies = get_session_cookies()
            challenge_res_result.response = basic_req.text
            challenge_res_result.userAgent = (
                get_session_headers()["User-Agent"]
                if "User-Agent" in get_session_headers()
                else ""
            )

        challenge_res.result = challenge_res_result

        res = V1ResponseBase({})
        res.status = challenge_res.status
        res.message = challenge_res.message
        res.solution = challenge_res.result
        return res
