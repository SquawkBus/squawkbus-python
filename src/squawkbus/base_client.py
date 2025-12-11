"""Squawkbus client"""

from __future__ import annotations
from abc import ABCMeta, abstractmethod
import asyncio
from asyncio import Event, Queue, Task
from base64 import b64encode
import logging
from typing import cast

from .data_packet import DataPacket
from .messages import (
    MessageType,
    Message,
    SubscriptionRequest,
    NotificationRequest,
    ForwardedSubscriptionRequest,
    MulticastData,
    UnicastData,
    AuthenticationRequest,
    AuthenticationResponse,
    ForwardedMulticastData,
    ForwardedUnicastData
)
from .types import MessageStream
from .utils import read_aiter

LOG = logging.getLogger(__name__)


class BaseClient(metaclass=ABCMeta):
    """Base client"""

    def __init__(
            self,
            stream: MessageStream,
            *,
            credentials: tuple[str, str] | None = None
    ) -> None:
        self._frame_stream = stream
        self._credentials = credentials
        self._read_queue: Queue[Message] = asyncio.Queue()
        self._write_queue: Queue[Message] = asyncio.Queue()
        self._stop_event = Event()
        self._process_task: Task[None] | None = None
        self._is_closed = Event()
        self._client_id: str | None = None

    @property
    def client_id(self) -> str | None:
        return self._client_id

    async def _authenticate(self) -> None:
        if self._credentials is None:
            method = "none"
            token = b""
        else:
            method = "basic"
            username, password = self._credentials
            credentials = f"{username}:{password}"
            token = b64encode(credentials.encode('utf-8'))

        authentication_request = AuthenticationRequest(method, token)

        LOG.debug("sending authentication with method '%s'", method)
        send_buf = authentication_request.serialize()
        await self._frame_stream.write(send_buf)

        LOG.debug("waiting for authentication response")
        recv_buf = await self._frame_stream.read()
        response = Message.deserialize(recv_buf)
        LOG.debug("received authentication response: %s", response)

        if response.message_type != MessageType.AUTHENTICATION_RESPONSE:
            raise ValueError("invalid message")

        message = cast(AuthenticationResponse, response)
        self._client_id = message.client_id

        LOG.debug("Authenticated")

    async def start(self) -> None:
        """Start handling messages"""

        await self._authenticate()
        self._process_task = asyncio.create_task(self._process_events())

    async def _process_events(self) -> None:
        LOG.debug('Started')

        async for message in read_aiter(self._read, self._write, self._dequeue, self._stop_event):
            if message.message_type == MessageType.FORWARDED_MULTICAST_DATA:
                await self._raise_multicast_data(
                    cast(ForwardedMulticastData, message)
                )
            elif message.message_type == MessageType.FORWARDED_UNICAST_DATA:
                await self._raise_unicast_data(
                    cast(ForwardedUnicastData, message)
                )
            elif message.message_type == MessageType.FORWARDED_SUBSCRIPTION_REQUEST:
                await self._raise_forwarded_subscription_request(
                    cast(ForwardedSubscriptionRequest, message)
                )
            else:
                raise RuntimeError(
                    f'Invalid message type {message.message_type}')

        is_faulted = not self._stop_event.is_set()
        if not is_faulted:
            await self._frame_stream.close()

        await self.on_closed(is_faulted)

        LOG.debug('Stopped')

    def stop(self) -> None:
        """Stop handling messages"""
        self._stop_event.set()

    async def wait_closed(self) -> None:
        if self._process_task is not None:
            await self._process_task

    def close(self) -> None:
        self._stop_event.set()

    async def _read_message(self) -> Message:
        buf = await self._frame_stream.read()
        message = Message.deserialize(buf)
        return message

    async def _raise_multicast_data(
            self,
            message: ForwardedMulticastData
    ) -> None:
        await self.on_data(
            message.user,
            message.host,
            message.topic,
            message.data_packets
        )

    async def _raise_unicast_data(
            self,
            message: ForwardedUnicastData
    ) -> None:
        await self.on_data(
            message.user,
            message.host,
            message.topic,
            message.data_packets
        )

    @abstractmethod
    async def on_data(
            self,
            user: str,
            host: str,
            topic: str,
            data_packets: list[DataPacket]
    ) -> None:
        """Called when data is received

        Args:
            user (str): The user name of the sender.
            host (str): The host from which the data was sent.
            feed (str): The feed name.
            topic (str): The topic name.
            data_packets (Optional[List[DataPacket]]): The data packets.
            is_image (bool): True if the data is considered an image.
        """

    async def _raise_forwarded_subscription_request(
            self,
            message: ForwardedSubscriptionRequest
    ) -> None:
        await self.on_forwarded_subscription_request(
            message.client_id,
            message.user,
            message.host,
            message.topic,
            message.count
        )

    @abstractmethod
    async def on_forwarded_subscription_request(
            self,
            client_id: str,
            user: str,
            host: str,
            topic: str,
            count: int
    ) -> None:
        """Called for a notification.

        Args:
            client_id (str): An identifier for the client.
            user (str): The name of the user that requested the subscription.
            host (str): The host from which the subscription was requested.
            feed (str): The feed name.
            count (int): The number of subscriptions.
        """

    @abstractmethod
    async def on_closed(self, is_faulted: bool) -> None:
        """Called when the connection has been closed

        Args:
            is_faulted (bool): If true the connection was closed by the server
        """

    async def publish(
            self,
            topic: str,
            data_packets: list[DataPacket]
    ) -> None:
        """Publish data to subscribers

        Args:
            topic (str): The topic name.
            data_packets (Optional[List[DataPacket]]): Th data packets.
        """
        await self._write_queue.put(
            MulticastData(
                topic,
                data_packets
            )
        )

    async def send(
            self,
            client_id: str,
            topic: str,
            data_packets: list[DataPacket]
    ) -> None:
        """Send data to a client

        Args:
            client_id (UUID): The clint id.
            topic (str): The topic name.
            data_packets (Optional[List[DataPacket]]): Th data packets.
        """
        await self._write_queue.put(
            UnicastData(
                client_id,
                topic,
                data_packets
            )
        )

    async def add_subscription(self, topic: str) -> None:
        """Add a subscription

        Args:
            topic (str): The topic name.
        """
        await self._write_queue.put(
            SubscriptionRequest(
                topic,
                True
            )
        )

    async def remove_subscription(self, topic: str) -> None:
        """Remove a subscription

        Args:
            topic (str): The topic name.
        """
        await self._write_queue.put(
            SubscriptionRequest(
                topic,
                False
            )
        )

    async def add_notification(self, topic_pattern: str) -> None:
        """Add a notification

        Args:
            topic_pattern (str): The topic_pattern name.
        """
        await self._write_queue.put(
            NotificationRequest(
                topic_pattern,
                True
            )
        )

    async def remove_notification(self, topic_pattern: str) -> None:
        """Remove a notification

        Args:
            topic_pattern (str): The topic_pattern name.
        """
        await self._write_queue.put(
            NotificationRequest(
                topic_pattern,
                False
            )
        )

    async def _read(self) -> None:
        buf = await self._frame_stream.read()
        message = Message.deserialize(buf)
        await self._read_queue.put(message)

    async def _dequeue(self) -> Message:
        message = await self._read_queue.get()
        return message

    async def _write(self):
        message = await self._write_queue.get()
        buf = message.serialize()
        await self._frame_stream.write(buf)
