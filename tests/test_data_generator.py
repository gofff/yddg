import pytest

from yddg.data_generator import YndxDiskDataGenerator
from tests.cases import PublicDiskCaseConstants as case_const


@pytest.fixture(params=[
        {
            'path_stream': True,
            'queue_size': 4
        },
        {
            'path_stream': True,
            'queue_size': 1
        },
        {
            'path_stream': False,
            'queue_size': 2
        },
])
def data_generator_object(request):
    urls = [case_const.CORRECT_URL, case_const.BAD_URL]
    path_stream = request.param['path_stream']
    queue_size = request.param['queue_size']
    return YndxDiskDataGenerator(urls = urls,
                                 max_files_in_path = 16,
                                 path_stream = path_stream,
                                 queue_size = queue_size)


def test_item_generator(data_generator_object):

    datagen = data_generator_object
    for item in datagen.item_generator():
        out_url, out_path = item[:2]
        assert out_url == case_const.CORRECT_URL
        assert out_path in case_const.CORRECT_OUT_PATHS