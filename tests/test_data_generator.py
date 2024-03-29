import pytest

from tests.cases import PublicDiskCaseConstants as case_const
from yddg.constants import aenumerate
from yddg.data_generator import YDDataGenerator

ONE_CASE_TIMEOUT = 10
NUM_PASSES = 3

async def check_one_pass(yddg, correct_result):
    results = set()
    async for item in yddg:
        results.add(item[1])
    assert results == set(correct_result)

async def check_multi_pass(yddg, num_passes):
    num_paths = len(case_const.CORRECT_OUT_PATHS)
    num_steps = num_passes * num_paths
    result = set()
    etalon = set(case_const.CORRECT_OUT_PATHS)
    async for i, item in aenumerate(yddg):
        if (i % num_paths) or not i:
            result.add(item[1])
        else:
            assert result == etalon
            result = {item[1]}
        if i >= num_steps:
            break

@pytest.mark.timeout(ONE_CASE_TIMEOUT)
@pytest.mark.asyncio
async def test_generator_wo_features():
    args = [[case_const.CORRECT_URL], case_const.CORRECT_FILES_NUM]
    kwargs = {"endless": False, "shuffle": False, "cache_paths": False}
    async with YDDataGenerator(*args, **kwargs) as yddg:
        await check_one_pass(yddg, case_const.CORRECT_OUT_PATHS)

@pytest.mark.timeout(NUM_PASSES * ONE_CASE_TIMEOUT)
@pytest.mark.asyncio
@pytest.mark.parametrize("cache_paths", [True, False])
async def test_generator_endless(cache_paths):
    args = [[case_const.CORRECT_URL], case_const.CORRECT_FILES_NUM]
    kwargs = {"endless": True, "shuffle": False, "cache_paths": cache_paths}
    async with YDDataGenerator(*args, **kwargs) as yddg:
        await check_multi_pass(yddg, NUM_PASSES)

@pytest.mark.timeout(2 * ONE_CASE_TIMEOUT)
@pytest.mark.asyncio
async def test_generator_shuffle():
    args = [[case_const.CORRECT_URL], case_const.CORRECT_FILES_NUM]
    kwargs = {"endless": True, "shuffle": True, "cache_paths": True}
    num_paths = len(case_const.CORRECT_OUT_PATHS)
    result = []
    async with YDDataGenerator(*args, **kwargs) as yddg:
        async for i, item in aenumerate(yddg):
            if i >= 2 * num_paths:
                break
            result.append(item[1])
        assert result[:num_paths] != result[num_paths:]

@pytest.mark.timeout(2 * ONE_CASE_TIMEOUT)
@pytest.mark.asyncio
@pytest.mark.parametrize(
        "exclude", ["folder_1", "jpg"]
    )
async def test_generator_exclude_names(exclude):
    exclude_regexp = r"\S*" + exclude + r"*"
    args = [[case_const.CORRECT_URL], case_const.CORRECT_FILES_NUM]
    kwargs = {"endless": False, "exclude_names": exclude_regexp}
    async with YDDataGenerator(*args, **kwargs) as yddg:
        await check_one_pass(yddg, [x for x in case_const.CORRECT_OUT_PATHS
                                       if exclude not in x])

@pytest.mark.filterwarnings("ignore: Bad request status*")
@pytest.mark.timeout(ONE_CASE_TIMEOUT)
@pytest.mark.asyncio
async def test_bad_url():
    args = [[case_const.BAD_URL], case_const.CORRECT_FILES_NUM]
    kwargs = {"endless": False, "shuffle": False, "cache_paths": False}
    async with YDDataGenerator(*args, **kwargs) as yddg:
        async for _ in yddg:
            assert False

@pytest.mark.timeout(ONE_CASE_TIMEOUT)
@pytest.mark.asyncio
async def test_nonasync_iterator_calls():
    args = [[case_const.CORRECT_URL], case_const.CORRECT_FILES_NUM]
    kwargs = {"endless": False, "shuffle": False, "cache_paths": False}
    async with YDDataGenerator(*args, **kwargs) as yddg:
        with pytest.raises(AssertionError) as _:
            next(yddg)
        with pytest.raises(AssertionError) as _:
            iter(yddg)
