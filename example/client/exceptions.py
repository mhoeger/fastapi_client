import json
from typing import Any, Dict, Optional

from httpx import AsyncResponse

MAX_CONTENT = 200


class ApiException(Exception):
    """Base class"""


class UnexpectedResponse(ApiException):
    def __init__(self, status_code: Optional[int], reason_phrase: str, content: bytes, headers: str) -> None:
        self.status_code = status_code
        self.reason_phrase = reason_phrase
        self.content = content
        self.headers = headers

    @staticmethod
    def for_response(response: AsyncResponse) -> "ApiException":
        return UnexpectedResponse(
            status_code=response.status_code,
            reason_phrase=response.reason_phrase,
            content=response.content,
            headers=response.headers,
        )

    def __str__(self) -> str:
        status_code_str = f"{self.status_code}" if self.status_code is not None else ""
        if self.reason_phrase == "" and self.status_code is not None:
            reason_phrase_str = "(Unrecognized Status Code)"
        else:
            reason_phrase_str = f"({self.reason_phrase})"
        status_str = f"{status_code_str} {reason_phrase_str}".strip()
        short_content = self.content if len(self.content) <= MAX_CONTENT else self.content[: MAX_CONTENT - 3] + b" ..."
        raw_content_str = f"Raw response content:\n{short_content}"
        return f"Unexpected Response: {status_str}\n{raw_content_str}"

    def structured(self) -> Dict[str, Any]:
        return json.loads(self.content)


class ApiRequestException(ApiException):
    def __init__(self, source: Exception):
        self.source = source