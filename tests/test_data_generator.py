import asyncio
import pytest

from tests.cases import PublicDiskCaseConstants as case_const
from yddg.data_generator import YndxDiskDataGenerator

@pytest.mark.asyncio
async def test_generator_wo_features():
    args = [[case_const.CORRECT_URL], case_const.CORRECT_FILES_NUM]
    kwargs = {"reusable": False, "shuffle": False, "endless": False}
    async with YndxDiskDataGenerator(*args, **kwargs) as yddg:
        results = set()
        async for item in yddg:
            assert item[1] in case_const.CORRECT_OUT_PATHS
            results.add(item[1])
        assert len(results) == len(case_const.CORRECT_OUT_PATHS)

#def test_generator_we_features():
#    asyncio.get_event_loop().run_until_complete(generator_wo_features())
