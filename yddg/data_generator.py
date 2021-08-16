import asyncio
import os
import random
from typing import Iterable, List, Union

import yddg.api_tasks as api_tasks
import yddg.constants as const
import yddg.custom_types as T


async def flush(queue: Union[T.YDiskPathQueue, T.ItemQueue], 
                by_none: bool = False) -> None:
    if by_none:
        while await queue.get() is not None:
            queue.task_done()
        queue.task_done()
    else:
        while not queue.empty():
            await queue.get()
            queue.task_done()

class YndxDiskDataGenerator(Iterable):

    def __init__(
        self,
        urls: List[str],
        max_files_in_path: int,
        reusable: bool = False,    # not delete paths
        shuffle: bool = False,    # shuffle paths inplace and in runtime
        endless: bool = False,    # cyclic repeat
        queue_size: int = const.DEFAULT_QUEUE_SIZE,
        exclude_names: str = '',
    ) -> None:
        self.urls = urls
        self.max_files = max_files_in_path
        self.reusable = reusable
        self.shuffle = shuffle
        self.endless = endless
        self.exclude_names = exclude_names

        self.paths: List[T.YDiskPath] = []
        self.paths_queue: T.YDiskPathQueue = asyncio.Queue(queue_size * 2)
        self.item_queue: T.ItemQueue = asyncio.Queue(queue_size)
        self.is_first_path_extract = True
        self.path_extract_stop = False
        self.path_extract_task: T.ExtractTask = None
        self.item_extract_task: T.ExtractTask = None 


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
                if not self.path_extract_stop:
                    await self.paths_queue.put(path)
                else:
                    break
            self.is_first_path_extract = False
            if not self.endless:
                self.path_extract_stop = True
        await self.paths_queue.put(None)

    async def start(self) -> None:
        self.path_extract_task = asyncio.ensure_future(
            self.__path_extracting())
        self.item_extract_task = asyncio.ensure_future(
            api_tasks.download_task(self.paths_queue, self.item_queue))

    async def stop(self) -> None:
        # flush paths queue
        self.path_extract_stop = True
        await flush(self.paths_queue)
        await self.paths_queue.put(None) # to stop item downloads

        # flush items queue
        if self.endless or not self.item_queue.empty():
            await flush(self.item_queue, by_none=True)

        # we cannot guarantee that paths_queue doesnt have
        # elements after None, so we must try to clear it
        await flush(self.paths_queue)
        await self.paths_queue.join()
        await self.item_queue.join()

    async def __anext__(self):
        item = await self.item_queue.get()
        self.item_queue.task_done()
        if item is not None:
            return item
        elif not self.endless:
            raise StopAsyncIteration
        else:
            # return next item
            item = await self.item_queue.get()
            self.item_queue.task_done()
            return item
        assert False, "Wrong state in yddg.__anext__"

    def __iter__(self):
        return self

    def __aiter__(self):
        return self

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, *excinfo):
        await self.stop()


async def main():
    urls = ['https://yadi.sk/d/FMbYkNAfcOYAzg?w=1']

    async with YndxDiskDataGenerator(urls,
                                     100,
                                     reusable=True,
                                     shuffle=True,
                                     endless=True) as yddg:
        counter = 0
        async for item in yddg:
            print(f"{counter} Result: {item[1]}")
            counter += 1
            if counter > 7:
                break


if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.get_event_loop().run_until_complete(main())
