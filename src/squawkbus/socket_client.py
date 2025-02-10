"""Callback client"""

from __future__ import annotations

from pathlib import Path
from ssl import SSLContext

from .callback_client import CallbackClient
from .socket_stream import SocketStream
from .utils import make_ssl_context


class SocketClient(CallbackClient):
    """Squawkbus client"""

    @classmethod
    async def create(
            cls,
            host: str = 'localhost',
            port: int = 8558,
            *,
            credentials: tuple[str, str] | None = None,
            ssl: SSLContext | str | Path | bool | None = None,
            auto_start: bool = True
    ) -> SocketClient:
        """Create a squawkbus client.

        Args:
            host (str): The server host. Defaults to localhost
            port (int): The server port. Defaults to 8558.
            credentials (tuple[str, str] | None, optional): Optional credentials.
                If specified this is a tuple of the username and password.
                Defaults to None.
            ssl (SSLContext | str | Path | bool | None, optional): An optional ssl
                parameter. If None or false, TLS is not used. If true a default
                ssl context is made. A string is used as the path to a bundle,
                for use with self signed certificates. Finally a pre-built
                SSLContext can be passed. Defaults to None.
            auto_start (bool, optional): If true automatically start the client.
                Defaults to True.

        Returns:
            SquawkbusClient: The squawkbus client
        """
        stream = await SocketStream.create(host, port, make_ssl_context(ssl))

        client = cls(stream, credentials=credentials)
        if auto_start:
            await client.start()

        return client
