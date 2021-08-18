import asyncio
from typing import TYPE_CHECKING, Optional, Tuple

YDiskPath = Tuple[str, str]

# TYPE_CHEKING need to avoid
#   TypeError: 'type' object is not subscriptable
# for generic classes in stubs but not at runtime
# fi look at:
# https://mypy.readthedocs.io/en/stable/runtime_troubles.html#runtime-troubles
if TYPE_CHECKING:
    ExtractTask = Optional[asyncio.Future[None]]
    YDiskPathQueue = asyncio.Queue[Optional[YDiskPath]]
    ItemQueue = asyncio.Queue[Optional[Tuple[str, str, bytes]]]
else:
    ExtractTask = asyncio.Future
    YDiskPathQueue = asyncio.Queue
    ItemQueue = asyncio.Queue
