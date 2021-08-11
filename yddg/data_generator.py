import multiprocessing as mp
import random
import time
from typing import (Any, List, Optional, Union, AsyncGenerator, Generator,
                    Iterable, Iterator)

import asyncio

import constants as const
import api_tasks as api_tasks




class YndxDiskDataGenerator(Iterable):

    def __init__(self,
                 urls: List[str],
                 max_files_in_path: int,
                 reusable: bool = False, # not delete paths
                 shuffle: bool = False, # shuffle paths inplace and in runtime
                 endless: bool = False, # cyclic repeat
                 queue_size: int = const.DEFAULT_QUEUE_SIZE,
                 exclude_names: str = '',) -> None:
        self.urls = urls
        self.max_files = max_files_in_path
        self.reusable = reusable
        self.shuffle = shuffle
        self.endless = endless
        self.exclude_names = exclude_names

        self.paths: List[str] = []
        self.paths_queue: asyncio.Queue[str] = asyncio.Queue(queue_size * 2)
        self.item_queue: asyncio.Queue[Any] = asyncio.Queue(queue_size)
        self.is_first_path_extract = True
        self.path_extract_stop = False
        self.path_extract_task = None
        self.item_extract_task = None
        
    async def __path_extracting(self) -> None:
        path_gen = None
        while not self.path_extract_stop:
            if len(self.paths):
                if self.shuffle:
                    random.shuffle(self.paths)
                path_gen = api_tasks.path_list_agen(self.paths)
            else:
                path_gen = api_tasks.parse_paths_task(self.urls,
                                                      self.max_files,
                                                      self.exclude_names)
            async for path in path_gen:
                if self.reusable and self.is_first_path_extract:
                    self.paths.append(path)
                print(f"Put {path[1]}")
                await self.paths_queue.put(path)

            self.is_first_path_extract = False
            if not self.endless:
                self.path_extract_stop = True
        await self.paths_queue.put(None)

    async def start(self) -> None:
        self.path_extract_task = asyncio.ensure_future(
                                    self.__path_extracting()
                                 )
        self.item_extract_task = asyncio.ensure_future(
                                    api_tasks.download_task(self.paths_queue,
                                                            self.item_queue)
                                 )

    async def stop(self) -> None:
        self.path_extract_stop = True
        if not self.path_extract_task.cancelled():
            self.path_extract_task.cancel()

        if self.item_queue.qsize():
            while await self.item_queue.get() is not None:
                self.item_queue.task_done()
            self.item_queue.task_done()

        if not self.item_extract_task.cancelled():
            self.item_extract_task.cancel()

    async def __anext__(self):
        item = await self.item_queue.get() 
        if item is not None:
            return item
        elif not self.endless:
            raise StopAsyncIteration
        else:
            return await self.item_queue.get()
        assert f"Wrong item and endless flag combination in yddg.__anext__"

    def __iter__(self):
        return self

    def __aiter__(self):
        return self

    def __del__(self) -> None:
        self.stop()
        #self.paths_queue.join()
        #self.item_queue.join()
   
async def main():
    urls = ['https://yadi.sk/d/FMbYkNAfcOYAzg?w=1']
    yddg = YndxDiskDataGenerator(urls, 100, reusable=True, shuffle=True, 
                                 endless=True)
    await yddg.start()
    counter = 0
    async for item in yddg:
        print(f"{counter} Result: {item[1]}")
        counter += 1
        if counter > 7:
            break   
    await yddg.stop()
'''
    await yddg.start()
    counter = 0
    async for item in yddg:
        print(f"{counter} Result: {item[1]}")
        counter += 1
        if counter > 10:
            break   
    yddg.stop()
'''

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())