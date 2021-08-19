import warnings
from typing import Any, AsyncGenerator, Tuple

DEFAULT_QUEUE_SIZE = 8


class REQ_STATUS:

    OK = 200


class YD_API:

    PUBLIC_URL = 'https://cloud-api.yandex.net/v1/disk/public/resources'
    PUBLIC_DOWNLOAD_URL = PUBLIC_URL + '/download'


def bad_request_warning(status_code: int, url: str, params: Any) -> None:

    warnings.warn(
        f'Bad request status ({status_code}) to ' +
        f'{url} with params: {params}',
        RuntimeWarning,
    )


async def aenumerate(
    agenerator: AsyncGenerator[Any, None]
) -> AsyncGenerator[Tuple[int, Any], None]:
    i: int = 0
    async for item in agenerator:
        yield i, item
        i += 1
