import requests
from typing import List, Tuple, Any
import multiprocessing as mp

import yddg.constants as const


class Downloader:


    def __init__(self) -> None:

        return


    def download_file(self, url: str, path: str) -> bytes:

        api_url = const.YD_API.PUBLIC_DOWNLOAD_URL
        params = {'public_key': url}
        if path:
            params['path'] = path
        resp = requests.get(api_url, params)
        if resp.status_code != requests.codes.ok:
            const.bad_request_warning(resp.status_code,
                                      api_url, params)
            return b''
        download_url = resp.json()['href']

        resp = requests.get(download_url)
        if resp.status_code != requests.codes.ok:
            const.bad_request_warning(resp.status_code,
                                      download_url, params = '')
            return b''

        return resp.content


    def download_stream(self, download_paths: List[Tuple[str, str]],
                        out_queue: mp.Queue) -> None:

        for url, path in download_paths:
            file_bytes = self.download_file(url, path)
            out_queue.put((url, path, file_bytes), block = True)
        out_queue.put(None, block = True)
        return


    def download_stream_from_stream(self, path_queue: mp.Queue,
                                    out_queue: mp.Queue) -> None:
        download_path = path_queue.get(block = True)
        while download_path is not None:
            url, path = download_path
            file_bytes = self.download_file(url, path)
            out_queue.put((url, path, file_bytes), block = True)
            download_path = path_queue.get(block = True)
        out_queue.put(None, block = True)
        return