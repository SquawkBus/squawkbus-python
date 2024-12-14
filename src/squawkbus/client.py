"""Callback client"""

from __future__ import annotations

import asyncio
from asyncio import Queue, StreamReader, StreamWriter
import logging
from ssl import SSLContext, Purpose, create_default_context
from typing import Callable, Awaitable

from .base_client import BaseClient
from .data_packet import DataPacket
from .messages import Message

LOGGER = logging.getLogger(__name__)

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
            host: str,
            port: int,
            *,
            credentials: tuple[str, str] | None = None,
            ssl: SSLContext | bool | None = None,
            auto_start: bool = True
    ) -> SquawkbusClient:
        """Create the client

        Args:
            host (str): The host name of the distributor.
            port (int): The distributor port
            credentials (Optional[tuple[str, str]], optional): Optional credentials. Defaults to None.
            ssl (Optional[SSLContext | bool], optional): The context for an ssl connection. Defaults to None.
            auto_start (Optional[bool], optional): Whether to start the client. Defaults to True.

        Returns:
            CallbackClient: The connected client.
        """
        if isinstance(ssl, bool):
            ssl = (
                create_default_context(Purpose.SERVER_AUTH)
                if ssl
                else None
            )

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
