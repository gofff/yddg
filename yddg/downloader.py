import multiprocessing as mp
from typing import List, Tuple

import aiohttp
import asyncio
import requests

import constants as const
from path_requester import PathRequester


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

    assert f"Wrong return statement in download_file({url}, {path})"
    return b''


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
        
'''
async def download_consumer(file_q):
    item = await file_q.get()
    file_q.task_done()
    while item is not None:
        print(f"downloaded: {item[0]} {item[1]}")
        item = await file_q.get()
        file_q.task_done()

async def test_downloader():
    path_q = asyncio.Queue()
    file_q = asyncio.Queue()
    pr = PathRequester(['https://yadi.sk/d/FMbYkNAfcOYAzg?w=1'], 1000, path_q)
    await asyncio.create_task(pr.run())
    await asyncio.create_task(download_task(path_q, file_q))
    await asyncio.create_task(download_consumer(file_q))
    await path_q.join()
    await file_q.join()


loop = asyncio.get_event_loop()
loop.run_until_complete(test_downloader())
'''
