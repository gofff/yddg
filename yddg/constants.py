import warnings
from typing import Any

import requests


class YD_API:

    PUBLIC_URL = 'https://cloud-api.yandex.net' + \
                 '/v1/disk/public/resources'
    PUBLIC_DOWNLOAD_URL = PUBLIC_URL + '/download'


def bad_request_warning(status_code: int, 
                        url: str, params: Any) -> None:

    warnings.warn(
            f'Bad request status ({status_code}) to ' + \
            f'{url} with params: {params}',
            RuntimeWarning
        )
