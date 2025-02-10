"""Types"""

from typing import Protocol


class MessageStream(Protocol):

    async def write(self, buf: bytes) -> None:
        ...

    async def read(self) -> bytes:
        ...

    async def close(self) -> None:
        ...
