from typing import Dict, List

saved_cookies: List[Dict[str, str]] = []
saved_headers = {}


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


def get_session_cookies() -> List[Dict[str, str]]:
    return saved_cookies


def get_session_headers():
    return saved_headers
