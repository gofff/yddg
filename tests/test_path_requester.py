import pytest
from yddg.path_requester import PathRequester
import multiprocessing as mp


def test_object_init():

    path_requester = PathRequester()


class TestPathRequesterAllPaths:


    def test_get_all_paths_method_empty_input(self):

        path_requester = PathRequester()
        out = path_requester.get_all_paths([])
        expected = []
        assert out == expected


class TestPathRequesterStreamPaths:


    def test_get_path_stream_method_noout(self):

        path_queue = mp.Queue(1)
        path_requester = PathRequester()
        out = path_requester.get_path_stream([], path_queue)
        assert out is None


    def test_get_path_stream_method_out_queue(self):

        path_queue = mp.Queue(1)
        val = 0
        path_queue.put(val, block = True)

        path_requester = PathRequester()
        path_requester.get_path_stream([], path_queue)
        
        out = path_queue.get(block = True)
        assert out == val

