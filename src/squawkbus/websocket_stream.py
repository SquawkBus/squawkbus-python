"""Websocket IO"""

from __future__ import annotations

from ssl import SSLContext

from websockets.asyncio.client import connect, ClientConnection


class WebsocketStream:

    def __init__(self, websocket: ClientConnection) -> None:
        self._websocket = websocket

    @classmethod
    async def create(
            cls,
            uri: str = 'ws://localhost:8533',
            ssl: SSLContext | None = None,
    ) -> WebsocketStream:
        websocket = await connect(uri, ssl=ssl)

        return WebsocketStream(websocket)

    async def write(self, buf: bytes) -> None:
        await self._websocket.send(buf, text=False)

    async def read(self) -> bytes:
        buf = await self._websocket.recv()
        if not isinstance(buf, bytes):
            raise ValueError("websocket received text - expected binary")
        return buf

    async def close(self) -> None:
        await self._websocket.close()
