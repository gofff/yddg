import multiprocessing as mp
from typing import Any, List

from yddg.downloader import Downloader
from yddg.path_requester import PathRequester


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
        self.out_queue: mp.Queue = mp.Queue(queue_size)

        if path_stream:

            path_queue: mp.Queue = mp.Queue(queue_size * 2)
            path_request_call = self.path_requester.get_path_stream
            self.path_request_proc = mp.Process(target=path_request_call,
                                                args=(urls, path_queue))
            self.path_request_proc.start()

            download_call = self.downloader.download_stream_from_stream
            self.download_proc = mp.Process(target=download_call,
                                            args=(path_queue, self.out_queue))
        else:

            path_list = self.path_requester.get_all_paths(urls)

            download_call_flist = self.downloader.download_stream
            self.download_proc = mp.Process(target=download_call_flist,
                                            args=(path_list, self.out_queue))

        self.download_proc.start()
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
