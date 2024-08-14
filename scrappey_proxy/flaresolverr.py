import logging
from typing import Callable

from scrappey_proxy import utils

STATUS_OK = "ok"
STATUS_ERROR = "error"

logger = logging.getLogger("gunicorn.error")


class ChallengeResolutionResultT:
    url: str | None = None
    status: int | None = None
    headers: dict | None = None
    response: str | None = None
    cookies: list | None = None
    userAgent: str | None = None

    def __init__(self, _dict):
        self.__dict__.update(_dict)


class ChallengeResolutionT:
    status: str | None = None
    message: str | None = None
    result: ChallengeResolutionResultT | None = None

    def __init__(self, _dict):
        self.__dict__.update(_dict)
        if self.result is not None:
            self.result = ChallengeResolutionResultT(self.result)


class V1RequestBase(object):
    cmd: str | None = None
    cookies: list | None = None
    maxTimeout: int | None = None
    proxy: dict | None = None
    session: str | None = None
    session_ttl_minutes: int | None = None
    headers: list | None = None  # deprecated v2.0.0, not used
    userAgent: str | None = None  # deprecated v2.0.0, not used
    # V1Request
    url: str | None = None
    postData: str | None = None
    returnOnlyCookies: bool | None = None
    download: bool | None = None  # deprecated v2.0.0, not used
    returnRawHtml: bool | None = None  # deprecated v2.0.0, not used

    def __init__(self, _dict):
        self.__dict__.update(_dict)


class V1ResponseBase(object):
    # V1ResponseBase
    status: str | None = None
    message: str | None = None
    session: str | None = None
    sessions: list[str] | None = None
    startTimestamp: int | None = None
    endTimestamp: int | None = None
    version: str | None = None
    # V1ResponseSolution
    solution: ChallengeResolutionResultT | None = None
    # hidden vars
    __error_500__: bool = False

    def __init__(self, _dict):
        self.__dict__.update(_dict)
        if self.solution is not None:
            self.solution = ChallengeResolutionResultT(self.solution)


def controller_v1_logic(
    req: V1RequestBase, get_handler: Callable[[V1RequestBase], V1ResponseBase]
) -> V1ResponseBase:
    if req.cmd is None:
        raise Exception("Request parameter 'cmd' is mandatory.")

    if req.maxTimeout is None or int(req.maxTimeout) < 1:
        req.maxTimeout = 60000

    res: V1ResponseBase
    if req.cmd == "request.get":
        res = get_handler(req)
    else:
        raise Exception(f"Request parameter 'cmd' = '{req.cmd}' is invalid.")

    return res


def controller_v1_handler(
    req: V1RequestBase, get_handler: Callable[[V1RequestBase], V1ResponseBase]
):
    res: V1ResponseBase
    logger.info(f"Incoming request => POST /v1 body: {utils.object_to_dict(req)}")
    try:
        res = controller_v1_logic(req, get_handler)
    except Exception as e:
        res = V1ResponseBase({})
        res.__error_500__ = True
        res.status = STATUS_ERROR
        res.message = f"Error: {e}"

    res.version = "3.0.0"
    return res
