import asyncio
from typing import Optional, Tuple

YDiskPath = Tuple[str, str]
ExtractTask = Optional[asyncio.Future[None]]
YDiskPathQueue = asyncio.Queue[Optional[YDiskPath]]
ItemQueue = asyncio.Queue[Optional[Tuple[str, str, bytes]]]
