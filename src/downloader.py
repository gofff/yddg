import requests
from typing import List, Tuple, Any
import multiprocessing as mp


class Downloader:


    def __init__(self) -> None:

        return


    def download_file(self, link: str, path: str) -> Any:

        return 0


    def download_stream(self, paths: List[Tuple[str, str]],
                        out_queue: mp.Queue) -> None:

        return


    def download_stream_from_stream(self, path_queue: mp.Queue,
                                    out_queue: mp.Queue) -> None:

        return