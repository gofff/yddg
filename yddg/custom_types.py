from typing import Tuple, Optional

import asyncio

YDiskPath = Tuple[str, str]
ExtractTask = Optional[asyncio.Future[None]]
YDiskPathQueue = asyncio.Queue[Optional[YDiskPath]]
ItemQueue = asyncio.Queue[Optional[Tuple[str, str, bytes]]]