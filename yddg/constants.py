import warnings
from typing import Any, AsyncGenerator, List, Tuple

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


async def path_list_agen(path_list: List[Any]) -> AsyncGenerator[Any, None]:
    for path in path_list:
        yield path


def event_loop_closed_workaround() -> None:
    import sys

    # thanks for workaround:
    # https://github.com/aio-libs/aiohttp/issues/4324#issuecomment-733884349
    if (sys.platform.startswith("win")
            and sys.version_info[2] < 10):
        from asyncio.proactor_events import _ProactorBasePipeTransport
        from functools import wraps

        def silence_del(func):
            @wraps(func)
            def wrapper(self, *args, **kwargs):
                try:
                    return func(self, *args, **kwargs)
                except RuntimeError as e:
                    if str(e) != 'Event loop is closed':
                        raise

            return wrapper

        _ProactorBasePipeTransport.__del__ = silence_del(
            _ProactorBasePipeTransport.__del__)
