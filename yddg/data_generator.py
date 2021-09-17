import asyncio
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


class YDDataGenerator(Iterable):
    """ Asynchronous generator to work with data from Yandex Disk
        storage (disk.yandex.ru) without saving items to long-term
        memory.

        In general YDDG
            * takes list with urls (only public urls now)
            * parses directory tree of each url
            * construct remote path sequence to return one-by-one
            * send request to get file bytes from path sequence
            * return file bytes when __anext__() is called

        Args:
            urls: list of urls to get files from
            max_files_in_path: maximum number of files
                in one directory (or folder), storage API requires
                this value
            endless: makes generator endless if True. Defaults to False
            shuffle: reorders return sequence with random
                if selected to True. Defaults to False
            cache_paths: saves path sequence inside to avoid repeats
                of directory tree parsing. It's usefull
                when dir-tree is constant and generator is endless.
                Defaults to False
            queue_size: size of queue that store downloaded files
                before yielding from generator. Defaults to 8.
                If you work with lightweight files or
                you have a large amount of memory, network and cpu
                ticks, you can increase queue_size. If you aim is
                resource saving -- decrease size
            exclude_names: string with regexp to compile re.Pattern.
                Paths whith fullmatchs with Pattern will be skipped

        Yields:
            (str, str, bytes) : (url, path, file-bytes)
            url - public url of downloaded file,
            path - path of downloaded file inside root dir from url,
            file-bytes - bytes of downloaded file

        Raises:
            RuntimeWarning: if request to storage API goes wrong

        Example:
            .. code-block:: python

                from yddg import YDDataGenerator
                async with YDDataGenerator(urls, max_files) as yddg:
                    async for item in yddg:
                        url, path, file_bytes = item
                        do_something(file_bytes)

    """

    def __init__(
        self,
        urls: List[str],
        max_files_in_path: int,
        endless: bool = False,    # cyclic repeat
        shuffle: bool = False,    # shuffle paths inplace and in runtime
        cache_paths: bool = False,    # not delete paths
        queue_size: int = const.DEFAULT_QUEUE_SIZE,
        exclude_names: str = '',
    ) -> None:
        self.urls = urls
        self.max_files = max_files_in_path
        self.endless = endless
        self.shuffle = shuffle
        self.cache_paths = cache_paths
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
                path_gen = const.path_list_agen(self.paths)
            else:
                path_gen = api_tasks.parse_paths_task(self.urls,
                                                      self.max_files,
                                                      self.exclude_names)
            async for path in path_gen:
                if self.cache_paths and self.is_first_path_extract:
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
        # To silence 'Event loop is closed' RuntimeError in Windows
        # and Python < 3.10
        # For more information read:
        # https://github.com/aio-libs/aiohttp/issues/4324
        const.event_loop_closed_workaround()

        self.path_extract_task = asyncio.ensure_future(
            self.__path_extracting())
        self.item_extract_task = asyncio.ensure_future(
            api_tasks.download_task(self.paths_queue, self.item_queue))

    async def stop(self) -> None:
        # flush paths queue
        self.path_extract_stop = True
        await flush(self.paths_queue)
        await self.paths_queue.put(None)    # to stop item downloads

        # flush items queue
        if self.endless or not self.item_queue.empty():
            await flush(self.item_queue, by_none=True)

        # we cannot guarantee that paths_queue doesnt have
        # elements after None, so we must try to clear it
        await flush(self.paths_queue)
        await self.paths_queue.join()
        await self.item_queue.join()

        if (self.path_extract_task is not None
                and not self.path_extract_task.cancelled()):
            self.path_extract_task.cancel()

        if (self.item_extract_task is not None
                and not self.item_extract_task.cancelled()):
            self.item_extract_task.cancel()

    async def __anext__(self):
        item = await self.item_queue.get()
        self.item_queue.task_done()
        if item is not None:
            return item
        elif not self.endless:
            raise StopAsyncIteration
        else:
            assert False, "Wrong state in yddg.__anext__"

    def __iter__(self):
        assert False, "Calling non-async __iter__"

    def __next__(self):
        assert False, "Calling non-async __next__"

    def __aiter__(self):
        return self

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, *excinfo):
        await self.stop()


"""
async def main():
    urls = ['https://yadi.sk/d/FMbYkNAfcOYAzg?w=1']

    async with YDDataGenerator(urls,
                                     100,
                                     cache_paths=True,
                                     shuffle=True,
                                     endless=True) as yddg:
        counter = 0
        async for item in yddg:
            print(f"{counter} Result: {item[1]}")
            counter += 1
            if counter > 7:
                break


if __name__ == "__main__":
    import os
    if os.name == "nt":
        asyncio.set_event_loop_policy(
            asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.get_event_loop().run_until_complete(main())
    else:
        asyncio.run(main())
"""
