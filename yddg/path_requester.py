import requests
from typing import List, Tuple, Dict, Union, Any
import multiprocessing as mp
import warnings

import yddg.constants as const


def YD_request_items(url: str, path: str,
                     max_files: int) -> List[Dict[str, str]]:

    api_url = const.YD_API.PUBLIC_URL
    params: Dict[str, Union[str, int]] = {
        'public_key' : url,
        'limit' : max_files
    }
    if len(path) > 1:
        params['path'] = path

    r = requests.get(api_url, params = params)
    if r.status_code != requests.codes.ok:
        const.bad_request_warning(r.status_code,
                                  api_url, params)
        return []

    resource = r.json()
    return resource['_embedded']['items']


def YD_get_required_files(items: List[Dict[str,str]], 
                          url: str, max_files: int) -> List[str]:

    files = []
    for item in items:
        if item['type'] == 'dir':
            nested_items = YD_request_items(url, item['path'], max_files)
            files.extend(YD_get_required_files(nested_items, url, 
                                               max_files))
        elif item['type'] == 'file': 
            files.append(item['path'])
    return files


def YD_get_files_from_url(url: str, max_files: int) -> List[str]:

    return YD_get_required_files(YD_request_items(url, '', max_files),
                                 url, max_files)


class PathRequester:


    def __init__(self, max_files_in_path: int) -> None:

        self.max_files = max_files_in_path
        return


    def get_all_paths(self,
                      urls: List[str]) -> List[Tuple[str, str]]:

        all_paths: List[Tuple[str, str]] = []
        for url in urls:
            cur_paths = YD_get_files_from_url(url, self.max_files)
            for path in cur_paths:
                all_paths.append((url, path))
        return all_paths


    def get_path_stream(self, urls: List[str],
                        path_queue: mp.Queue) -> None:

        for url in urls:
            cur_paths = YD_get_files_from_url(url, self.max_files)
            for path in cur_paths:
                path_queue.put((url, path), block = True)
        path_queue.put(None, block = True)
        return