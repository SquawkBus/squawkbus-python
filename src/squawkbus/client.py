"""Callback client"""

from __future__ import annotations

import asyncio
from asyncio import Queue, StreamReader, StreamWriter
from pathlib import Path
from ssl import SSLContext, Purpose, create_default_context
from typing import Callable, Awaitable

from .base_client import BaseClient
from .data_packet import DataPacket
from .messages import Message


DataHandler = Callable[
    [str, str, str, list[DataPacket]],
    Awaitable[None]
]
NotificationHandler = Callable[
    [str, str, str, str, bool],
    Awaitable[None]
]
ClosedHandler = Callable[
    [bool],
    Awaitable[None]
]


class SquawkbusClient(BaseClient):
    """Squawkbus client"""

    def __init__(
            self,
            reader: StreamReader,
            writer: StreamWriter,
            *,
            credentials: tuple[str, str] | None = None
    ) -> None:
        super().__init__(reader, writer, credentials=credentials)
        self._data_handlers: list[DataHandler] = []
        self._notification_handlers: list[NotificationHandler] = []
        self._closed_handlers: list[ClosedHandler] = []
        self._read_queue: Queue[Message] = Queue()
        self._write_queue: Queue[Message] = Queue()

    @classmethod
    async def create(
            cls,
            host: str = 'localhost',
            port: int = 8558,
            *,
            credentials: tuple[str, str] | None = None,
            ssl: SSLContext | str | Path | bool | None = None,
            auto_start: bool = True
    ) -> SquawkbusClient:
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
        if isinstance(ssl, (bool, str, Path)):
            cafile = ssl if isinstance(ssl, (str, Path)) else None
            ssl = create_default_context(Purpose.SERVER_AUTH)
            if cafile is not None:
                ssl.load_verify_locations(cafile)

        reader, writer = await asyncio.open_connection(host, port, ssl=ssl)

        client = cls(reader, writer, credentials=credentials)
        if auto_start:
            await client.start()

        return client

    @property
    def data_handlers(self) -> list[DataHandler]:
        """The list of handlers called when data is received.

        Returns:
            list[DataHandler]: The list of handlers
        """
        return self._data_handlers

    @property
    def notification_handlers(self) -> list[NotificationHandler]:
        """The list of handlers called when a notification is received

        Returns:
            list[NotificationHandler]: The list of handlers
        """
        return self._notification_handlers

    @property
    def closed_handlers(self) -> list[ClosedHandler]:
        """The list of handlers called when a connection is closed

        Returns:
            List[ClosedHandler]: The list of handlers
        """
        return self._closed_handlers

    async def on_data(
            self,
            user: str,
            host: str,
            topic: str,
            data_packets: list[DataPacket]
    ) -> None:
        for handler in self._data_handlers:
            await handler(
                user,
                host,
                topic,
                data_packets,
            )

    async def on_forwarded_subscription_request(
            self,
            client_id: str,
            user: str,
            host: str,
            topic: str,
            is_add: bool
    ) -> None:
        for handler in self._notification_handlers:
            await handler(
                client_id,
                user,
                host,
                topic,
                is_add
            )

    async def on_closed(self, is_faulted: bool) -> None:
        for handler in self._closed_handlers:
            await handler(is_faulted)
