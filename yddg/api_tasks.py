import asyncio
import re
from collections import deque
from typing import Any, AsyncGenerator, List

import aiohttp

import yddg.constants as const
import yddg.custom_types as T


async def download_file(session: aiohttp.ClientSession, url: str,
                        path: str) -> bytes:
    download_url = ""
    api_url = const.YD_API.PUBLIC_DOWNLOAD_URL
    params = {
        'public_key': url,
        'path': path,
    }
    async with session.get(api_url, params=params) as resp:
        if resp.status != const.REQ_STATUS.OK:
            const.bad_request_warning(resp.status, api_url, params)
            return b''

        resp_json = await resp.json()
        download_url = resp_json['href']

    async with session.get(download_url) as resp:
        if resp.status != const.REQ_STATUS.OK:
            const.bad_request_warning(resp.status, download_url, params="")
            return b''
        return await resp.content.read()

    assert False, f"Wrong return statement in download_file({url}, {path})"
    return b''


async def get_items(session: aiohttp.ClientSession, url: str, path: str,
                    max_files: int) -> Any:
    api_url = const.YD_API.PUBLIC_URL
    params = {
        'public_key': url,
        'limit': max_files,
        'path': path,
    }

    async with session.get(api_url, params=params) as resp:
        if resp.status != const.REQ_STATUS.OK:
            const.bad_request_warning(resp.status, api_url, params)
            return []
        resp_json = await resp.json()
        return resp_json['_embedded']['items']


async def download_task(path_queue: asyncio.Queue,
                        out_queue: asyncio.Queue) -> None:
    async with aiohttp.ClientSession() as session:
        url_path = await path_queue.get()
        path_queue.task_done()
        while url_path is not None:
            content = await download_file(session, *url_path)
            await out_queue.put((*url_path, content))
            url_path = await path_queue.get()
            path_queue.task_done()
    await out_queue.put(None)


async def parse_paths_task(
        urls: List[str],
        max_files_in_path: int,
        exclude_names: str = '') -> AsyncGenerator[T.YDiskPath, None]:
    path_stack = deque([(url, '') for url in urls])
    skip_filter = re.compile(exclude_names) if exclude_names else None

    async with aiohttp.ClientSession() as session:
        while len(path_stack):
            cur_url, cur_path = path_stack.popleft()
            items = await get_items(session, cur_url, cur_path,
                                    max_files_in_path)
            for item in items:
                path = item['path']
                if (skip_filter is not None
                        and skip_filter.fullmatch(path) is not None):
                    continue
                url_path = (cur_url, path)
                if item['type'] == 'dir':
                    path_stack.appendleft(url_path)
                elif item['type'] == 'file':
                    yield url_path
                else:
                    assert f"""Bad path item type {item['type']} with
                            requested path {url_path}"""
                    pass
    # sometimes in tests ClientSession doesnt have time to close
    # but commnd after with fix this situation. idk why
    return


async def path_list_agen(
        path_list: List[T.YDiskPath]) -> AsyncGenerator[T.YDiskPath, None]:
    for path in path_list:
        yield path
