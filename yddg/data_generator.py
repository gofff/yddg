import multiprocessing as mp
import time
from typing import Any, List, Optional

from yddg.downloader import Downloader
from yddg.path_requester import PathRequester

#mp.set_start_method('fork')

class YndxDiskDataGenerator:

    def __init__(self,
                 urls: List[str],
                 max_files_in_path: int,
                 path_stream: bool = False,
                 queue_size: int = 2,
                 exclude_names: str = '') -> None:

        self.path_stream = path_stream
        self.path_requester = PathRequester(max_files_in_path, exclude_names)

        self.downloader = Downloader()
        self.download_proc: Optional[mp.Process] = None

        self.queue_size = queue_size
        self.out_queue: mp.Queue[Any] = mp.Queue(queue_size)

        self.__start_process__(urls)

    def __start_process__(self, urls: List[str]) -> None:

        print('Begin start processes')
        if self.path_stream:

            path_queue: mp.Queue[Any] = mp.Queue(self.queue_size * 2)
            path_request_call = self.path_requester.get_path_stream
            self.path_request_proc = mp.Process(target=path_request_call,
                                                args=(urls, path_queue))
            print('Try to start path requester process with path-stream')
            self.path_request_proc.start()
            print('Started')

            download_call = self.downloader.download_stream_from_stream
            self.download_proc = mp.Process(target=download_call,
                                            args=(path_queue, self.out_queue))
        else:

            path_list = self.path_requester.get_all_paths(urls)

            download_from_list_call = self.downloader.download_stream
            self.download_proc = mp.Process(target=download_from_list_call,
                                            args=(path_list, self.out_queue))

        print('Try to start downloader')
        self.download_proc.start()
        #time.sleep(5)
        print('Started')
        return

    def item_generator(self) -> Any:

        item = self.out_queue.get(block=True)
        while item is not None:
            yield item
            item = self.out_queue.get(block=True)

    def __del__(self):

        if self.path_stream:
            self.path_request_proc.join()
        self.download_proc.join()
