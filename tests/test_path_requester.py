import pytest
import multiprocessing as mp


import yddg.path_requester as path_requester
from tests.cases import PublicDiskCaseConstants as case_const


@pytest.fixture
def correct_public_test_data():
    return {
            'url': case_const.CORRECT_URL,
            'max_files': case_const.CORRECT_FILES_NUM
           }


def test_correct_out_YD_request_items(correct_public_test_data):

    url = correct_public_test_data['url']
    max_files = correct_public_test_data['max_files']
    out = path_requester.YD_request_items(url, '', max_files)
    
    assert out is not None
    assert len(out)
    assert len(out[0]['name'])
    assert out[0]['type'] in ['dir', 'file']


@pytest.fixture(params=[
        {
            'url': case_const.CORRECT_URL,
            'max_files': 0
        },
        {
            'url': case_const.BAD_URL,
            'max_files': case_const.CORRECT_FILES_NUM
        },
])
def bad_public_test_data(request):
    return request.param


def test_bad_out_YD_request_items(bad_public_test_data):

    url = bad_public_test_data['url']
    max_files = bad_public_test_data['max_files']
    out = path_requester.YD_request_items(url, '', max_files)
    
    assert out is not None
    assert not len(out)


@pytest.fixture
def correct_test_item():
    return [{
            'type': 'dir',
            'path': ''
            }]


@pytest.fixture(params = [
        {
            'type': 'unknown',
            'path': ''
        },
        {
            'type': 'dir',
            'path': 'not_exist_path/'
        }
    ])
def bad_test_item(request):
    return [request.param]


@pytest.fixture
def correct_out_paths():
    return case_const.CORRECT_OUT_PATHS


def test_correct_out_YD_get_required_files(correct_test_item,
                                           correct_public_test_data,
                                           correct_out_paths):

    url = correct_public_test_data['url']
    max_files = correct_public_test_data['max_files']
    out = path_requester.YD_get_required_files(correct_test_item,
                                               url, max_files)

    assert len(out)
    # Have not empty strings
    assert not [p for p in out 
                  if p not in case_const.CORRECT_OUT_PATHS]


def test_bad_out_YD_get_required_files(bad_test_item,
                                       bad_public_test_data,
                                       correct_out_paths):

    url = bad_public_test_data['url']
    max_files = bad_public_test_data['max_files']
    out = path_requester.YD_get_required_files(bad_test_item,
                                               url, max_files)

    assert not len(out)


@pytest.fixture
def path_requester_object():

    files_num = case_const.CORRECT_FILES_NUM
    return path_requester.PathRequester(max_files_in_path = files_num)


@pytest.fixture
def url_list():
    return [case_const.CORRECT_URL, case_const.BAD_URL]


class TestPathRequester:


    def test_get_all_paths(self, 
                           path_requester_object, url_list):

        pr = path_requester_object
        out = pr.get_all_paths(url_list)

        assert not [p for p in out 
                      if (p[1] not in case_const.CORRECT_OUT_PATHS or
                          p[0] != case_const.CORRECT_URL)]


    def test_get_path_stream(self, 
                             path_requester_object, url_list):

        pr = path_requester_object

        queue = mp.Queue(1)
        process = mp.Process(target = pr.get_path_stream, 
                             args=(url_list, queue,))
        process.start()

        for i in range(len(case_const.CORRECT_OUT_PATHS)):
            queue_out = queue.get(block = True)
            assert queue_out is not None
            assert queue_out[0] == case_const.CORRECT_URL
            assert queue_out[1] in case_const.CORRECT_OUT_PATHS

        assert queue.get(block = True) is None

        process.join()

    











