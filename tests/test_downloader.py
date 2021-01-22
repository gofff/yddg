import pytest
import multiprocessing as mp

from yddg.downloader import Downloader
from tests.cases import PublicDiskCaseConstants as case_const


def path_puller(queue):

    for path in case_const.CORRECT_OUT_PATHS:
        queue.put((case_const.CORRECT_URL, path), block = True)
    queue.put(None)


def line_counter(file_queue):

    counter = 0
    output = file_queue.get(block = True)
    while output is not None:
        url, path, file_bytes = output
        if '.txt' in path:
            decoded_output = file_bytes.decode('utf-8')
            words = decoded_output.split('\n')
            counter += len(words)
        output = file_queue.get(block = True)
    return counter


class TestDownloader:


    def test_download_file(self):

        dl = Downloader()
        input_url = case_const.CORRECT_URL
        input_path = case_const.PATH_FILE_1
        output = dl.download_file(input_url, input_path)

        decoded_output = output.decode('utf-8')
        decoded_output = decoded_output.replace('\r', '')
        assert decoded_output == case_const.CONTENT_FILE_1


    def test_download_stream(self):

        dl = Downloader()
        dl_paths = [(case_const.CORRECT_URL, p) 
                    for p in case_const.CORRECT_OUT_PATHS]
        out_queue = mp.Queue(2)
        dl_process = mp.Process(target = dl.download_stream,
                                args = (dl_paths, out_queue,))
        dl_process.start()

        assert line_counter(out_queue) == case_const.LINES_IN_TXTS

        dl_process.join()


    def test_download_stream_from_stream(self):

        dl = Downloader()
        in_queue = mp.Queue(2)
        pp_process = mp.Process(target = path_puller,
                                args = (in_queue,))

        out_queue = mp.Queue(2)
        dl_process = mp.Process(target = dl.download_stream_from_stream,
                                args = (in_queue, out_queue,))

        pp_process.start()
        dl_process.start()

        assert line_counter(out_queue) == case_const.LINES_IN_TXTS

        pp_process.join()
        dl_process.join()
