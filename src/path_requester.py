import requests
from typing import List, Tuple
import multiprocessing as mp


class PathRequester:


    def __init__(self) -> None:

        return


    def get_all_paths(self,
                      links: List[str]) -> List[Tuple[str, str]]:

        return []


    def get_path_stream(self, links: List[str],
                        path_queue: mp.Queue) -> None:

        return