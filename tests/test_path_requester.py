import sys
sys.path.append('./yddg')

import pytest
import multiprocessing as mp


import yddg.path_requester as path_requester


CORRECT_URL = 'https://yadi.sk/d/FMbYkNAfcOYAzg?w=1'
BAD_URL = ''
CORRECT_OUT_PATHS = ['/folder_1/avo.jpg', 
                     '/folder_1/file_2.txt', 
                     '/folder_2/file_3.txt', 
                     '/folder_2/file_4.txt', 
                     '/file_1.txt']

@pytest.fixture
def correct_public_test_data():
    return {
            'url': CORRECT_URL,
            'max_files': 1000
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
            'url': CORRECT_URL,
            'max_files': 0
        },
        {
            'url': BAD_URL,
            'max_files': 1000
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
    return CORRECT_OUT_PATHS


def test_correct_out_YD_get_required_files(correct_test_item,
                                           correct_public_test_data,
                                           correct_out_paths):

    url = correct_public_test_data['url']
    max_files = correct_public_test_data['max_files']
    out = path_requester.YD_get_required_files(correct_test_item,
                                               url, max_files)

    assert len(out)
    # Have not empty strings
    assert not len([p for p in out if len(p) == 0])\


def test_bad_out_YD_get_required_files(bad_test_item,
                                       bad_public_test_data,
                                       correct_out_paths):

    url = bad_public_test_data['url']
    max_files = bad_public_test_data['max_files']
    out = path_requester.YD_get_required_files(bad_test_item,
                                               url, max_files)

    assert not len(out)









