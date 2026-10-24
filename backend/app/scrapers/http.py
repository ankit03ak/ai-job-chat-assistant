import logging
import time
from collections.abc import Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

logger = logging.getLogger(__name__)


class SourceFetchError(RuntimeError):
    """Raised when a permitted source cannot be fetched safely."""


def fetch_json(
    url: str,
    *,
    timeout: float = 15,
    retries: int = 2,
    user_agent: str = "AIJobAssistant/0.1",
    sleep: Callable[[float], None] = time.sleep,
) -> bytes:
    for attempt in range(retries + 1):
        try:
            request = Request(url, headers={"User-Agent": user_agent, "Accept": "application/json"})
            with urlopen(request, timeout=timeout) as response:
                return response.read()
        except HTTPError as exc:
            if exc.code in {403, 429}:
                raise SourceFetchError(f"Source denied or rate-limited request ({exc.code})") from exc
            if exc.code < 500 or attempt == retries:
                raise SourceFetchError(f"Source returned HTTP {exc.code}") from exc
        except URLError as exc:
            if attempt == retries:
                raise SourceFetchError("Source could not be reached") from exc
        delay = 2**attempt
        logger.warning("Retrying source request after %.1f seconds", delay)
        sleep(delay)
    raise SourceFetchError("Source request failed")
