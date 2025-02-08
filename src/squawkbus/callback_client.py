"""Callback client"""

from __future__ import annotations

from asyncio import Queue
from typing import Callable, Awaitable

from .base_client import BaseClient
from .data_packet import DataPacket
from .messages import Message
from .types import MessageStream


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


class CallbackClient(BaseClient):
    """Squawkbus client"""

    def __init__(
            self,
            stream: MessageStream,
            *,
            credentials: tuple[str, str] | None = None
    ) -> None:
        super().__init__(stream, credentials=credentials)
        self._data_handlers: list[DataHandler] = []
        self._notification_handlers: list[NotificationHandler] = []
        self._closed_handlers: list[ClosedHandler] = []
        self._read_queue: Queue[Message] = Queue()
        self._write_queue: Queue[Message] = Queue()

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
