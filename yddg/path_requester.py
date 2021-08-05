from collections import deque
import multiprocessing as mp
import re
import random
from typing import Dict, List, Tuple, Union, Any, Optional

import aiohttp
import asyncio
import requests

import constants as const

async def _get_items(session: aiohttp.ClientSession, url: str, path: str, 
                     max_files: int) -> Any:
    api_url = const.YD_API.PUBLIC_URL
    params: Dict[str, Union[str, int]] = {
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



class PathRequester:

    def __init__(self,
                 urls: List[str],
                 max_files_in_path: int,
                 out_queue: asyncio.Queue,
                 exclude_names: str = '') -> None:

        self.path_stack = deque([(url, '') for url in urls])
        self.max_files = max_files_in_path
        self.out_queue = out_queue
        self.skip_filter: Optional[re.Pattern] = None
        if exclude_names:
            self.skip_filter = re.compile(exclude_names)

    async def run(self) -> None:

        async with aiohttp.ClientSession() as session:

            while len(self.path_stack):
                cur_url, cur_path = self.path_stack.popleft()
                items = await _get_items(session, cur_url, cur_path, 
                                         self.max_files)
                for item in items:
                    path = item['path']
                    if (self.skip_filter is not None
                            and self.skip_filter.fullmatch(path) is not None):
                        continue
                    url_path = (cur_url, path)
                    if item['type'] == 'dir':
                        self.path_stack.appendleft(url_path)
                    elif item['type'] == 'file':
                        #yield url_path
                        await self.out_queue.put(url_path)
                    else:
                        assert f"""Bad path item type {item['type']} with 
                                requested path {url_path}"""
                        pass
            await self.out_queue.put(None)
'''
async def consumer(q):
    item = await q.get()
    q.task_done()
    while item is not None:
        print(f"{item} get")
        item = await q.get()
        q.task_done()

async def test():
    q = asyncio.Queue()
    pr = PathRequester(['https://yadi.sk/d/FMbYkNAfcOYAzg?w=1'], 1000, q)
    producer_task = await asyncio.create_task(pr.run())
    consumer_task = await asyncio.create_task(consumer(q))
    await q.join() 
    

loop = asyncio.get_event_loop()
loop.run_until_complete(test())
'''     
