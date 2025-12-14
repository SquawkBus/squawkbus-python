"""Messages"""

from __future__ import annotations

from abc import ABCMeta, abstractmethod
from enum import Enum
from typing import Any

from .data_packet import DataPacket
from .data_reader import DataReader
from .data_writer import DataWriter


class MessageType(Enum):
    """Message types"""
    AUTHENTICATION_REQUEST = 1
    AUTHENTICATION_RESPONSE = 2
    MULTICAST_DATA = 3
    UNICAST_DATA = 4
    FORWARDED_SUBSCRIPTION_REQUEST = 5
    NOTIFICATION_REQUEST = 6
    SUBSCRIPTION_REQUEST = 7
    FORWARDED_MULTICAST_DATA = 8
    FORWARDED_UNICAST_DATA = 9


class Message(metaclass=ABCMeta):
    """Message Base Class"""

    def __init__(self, message_type: MessageType) -> None:
        self.message_type = message_type

    @classmethod
    def deserialize(cls, buf: bytes) -> Message:
        """Read a messages

        Args:
            reader (DataReader): The data reader.

        Raises:
            RuntimeError: When the message type is unknown.

        Returns:
            Message: The message.
        """
        reader = DataReader(buf)

        message_type = cls._read_header(reader)

        if message_type == MessageType.AUTHENTICATION_REQUEST:
            return AuthenticationRequest.read_body(reader)
        elif message_type == MessageType.AUTHENTICATION_RESPONSE:
            return AuthenticationResponse.read_body(reader)
        elif message_type == MessageType.MULTICAST_DATA:
            return MulticastData.read_body(reader)
        elif message_type == MessageType.UNICAST_DATA:
            return UnicastData.read_body(reader)
        elif message_type == MessageType.FORWARDED_SUBSCRIPTION_REQUEST:
            return ForwardedSubscriptionRequest.read_body(reader)
        elif message_type == MessageType.NOTIFICATION_REQUEST:
            return NotificationRequest.read_body(reader)
        elif message_type == MessageType.SUBSCRIPTION_REQUEST:
            return SubscriptionRequest.read_body(reader)
        elif message_type == MessageType.FORWARDED_MULTICAST_DATA:
            return ForwardedMulticastData.read_body(reader)
        elif message_type == MessageType.FORWARDED_UNICAST_DATA:
            return ForwardedUnicastData.read_body(reader)
        else:
            raise RuntimeError(f'Invalid message type {message_type}')

    @classmethod
    def _read_header(cls, reader: DataReader) -> MessageType:
        """Read the message header"""
        message_type = reader.read_byte()
        return MessageType(message_type)

    def write_header(self, writer: DataWriter) -> None:
        """Write the message header

        Args:
            writer (DataWriter): The data writer
        """
        writer.write_byte(self.message_type.value)

    @abstractmethod
    def write_body(self, writer: DataWriter) -> None:
        """Write the message body

        Args:
            writer (DataWriter): The data writer
        """

    def serialize(self) -> bytes:
        writer = DataWriter()
        self.write_header(writer)
        self.write_body(writer)
        return bytes(writer.buf)

    @classmethod
    @abstractmethod
    def read_body(cls, reader: DataReader) -> Message:
        """Read message the body

        Args:
            reader (DataReader): The data reader

        Returns:
            Message: The message.
        """


class AuthenticationRequest(Message):
    """An authentication request message"""

    def __init__(
            self,
            method: str,
            credentials: bytes
    ) -> None:
        """A request for authentication.

        Args:
            method (str): The authentication method.
            credentials (bytes): The credentials.
        """
        super().__init__(MessageType.AUTHENTICATION_REQUEST)
        self.method = method
        self.credentials = credentials

    @classmethod
    def read_body(cls, reader: DataReader) -> Message:
        method = reader.read_string()
        credentials = reader.read_byte_array()
        return AuthenticationRequest(method, credentials)

    def write_body(self, writer: DataWriter) -> None:
        writer.write_string(self.method)
        writer.write_byte_array(self.credentials)

    def __repr__(self):
        return f'AuthenticationRequest({self.method!r},{self.credentials!r})'

    def __str__(self) -> str:
        return f'{self.method=},{self.credentials=}'

    def __eq__(self, value: Any) -> bool:
        return (
            isinstance(value, AuthenticationRequest) and
            self.method == value.method and
            self.credentials == value.credentials
        )


class AuthenticationResponse(Message):
    """An authentication response"""

    def __init__(
            self,
            client_id: str,
    ) -> None:
        """The response to an authentication request.

        Args:
            client_id (str): The id for the client, assigned by the broker.
        """
        super().__init__(MessageType.AUTHENTICATION_RESPONSE)
        self.client_id = client_id

    @classmethod
    def read_body(cls, reader: DataReader) -> Message:
        client_id = reader.read_string()
        return AuthenticationResponse(client_id)

    def write_body(self, writer: DataWriter) -> None:
        writer.write_string(self.client_id)

    def __repr__(self):
        return f'AuthenticationResponse({self.client_id!r})'

    def __str__(self) -> str:
        return f'{self.client_id=}'

    def __eq__(self, value: Any) -> bool:
        return (
            isinstance(value, AuthenticationResponse) and
            self.client_id == value.client_id
        )


class MulticastData(Message):
    """A multicast data message"""

    def __init__(
            self,
            topic: str,
            data_packets: list[DataPacket]
    ) -> None:
        """A multicast data message.

        Args:
            topic (str): The topic name
            data_packets (Optional[List[DataPacket]]): The data packets.
        """
        super().__init__(MessageType.MULTICAST_DATA)
        self.topic = topic
        self.data_packets = data_packets

    @classmethod
    def read_body(cls, reader: DataReader) -> MulticastData:
        topic = reader.read_string()
        data_packets = reader.read_data_packet_array()
        return MulticastData(topic, data_packets)

    def write_body(self, writer: DataWriter) -> None:
        writer.write_string(self.topic)
        writer.write_data_packet_array(self.data_packets)

    def __repr__(self) -> str:
        return f'MulticastData({self.topic!r},{self.data_packets!r})'

    def __str__(self) -> str:
        return f'{self.topic=},{self.data_packets=}'

    def __eq__(self, value: Any) -> bool:
        return (
            isinstance(value, MulticastData) and
            self.topic == value.topic and
            self.data_packets == value.data_packets
        )


class UnicastData(Message):
    """A unicast data message"""

    def __init__(
            self,
            client_id: str,
            topic: str,
            data_packets: list[DataPacket]
    ) -> None:
        """A unicast data message.

        Args:
            client_id (UUID): The client identifier.
            topic (str): Thee topic name
            data_packets (Optional[List[DataPacket]]): The data packets
        """
        super().__init__(MessageType.UNICAST_DATA)
        self.client_id = client_id
        self.topic = topic
        self.data_packets = data_packets

    @classmethod
    def read_body(cls, reader: DataReader) -> UnicastData:
        client_id = reader.read_string()
        topic = reader.read_string()
        data_packets = reader.read_data_packet_array()
        return UnicastData(client_id, topic, data_packets)

    def write_body(self, writer: DataWriter) -> None:
        writer.write_string(self.client_id)
        writer.write_string(self.topic)
        writer.write_data_packet_array(self.data_packets)

    def __repr__(self) -> str:
        return f'UnicastData({self.client_id!r},{self.topic!r},{self.data_packets!r})'

    def __str__(self) -> str:
        return f'{self.client_id=},{self.topic=},{self.data_packets=}'

    def __eq__(self, value: Any) -> bool:
        return (
            isinstance(value, UnicastData) and
            self.client_id == value.client_id and
            self.topic == value.topic and
            self.data_packets == value.data_packets
        )


class ForwardedSubscriptionRequest(Message):
    """A forwarded subscription request"""

    def __init__(
            self,
            host: str,
            user: str,
            client_id: str,
            topic: str,
            count: int
    ) -> None:
        """A forwarded subscription request.

        Args:
            host (str): The host from which the request was made.
            user (str): The name of the user that requested the subscription.
            client_id (str): The identifier for the client that made the request.
            topic (str): The topic name.
            count (int): The number of subscriptions.
        """
        super().__init__(MessageType.FORWARDED_SUBSCRIPTION_REQUEST)
        self.host = host
        self.user = user
        self.client_id = client_id
        self.topic = topic
        self.count = count

    @classmethod
    def read_body(cls, reader: DataReader) -> ForwardedSubscriptionRequest:
        host = reader.read_string()
        user = reader.read_string()
        client_id = reader.read_string()
        topic = reader.read_string()
        count = reader.read_unsigned_int()
        return ForwardedSubscriptionRequest(host, user, client_id, topic, count)

    def write_body(self, writer: DataWriter) -> None:
        writer.write_string(self.host)
        writer.write_string(self.user)
        writer.write_string(self.client_id)
        writer.write_string(self.topic)
        writer.write_unsigned_int(self.count)

    def __repr__(self) -> str:
        # pylint: disable=line-too-long
        return f'ForwardedSubscriptionRequest({self.host!r},{self.user!r},{self.client_id!r},{self.topic!r},{self.count!r})'

    def __str__(self) -> str:
        # pylint: disable=line-too-long
        return f'{self.host=},{self.user=},{self.client_id=},{self.topic=},{self.count=}'

    def __eq__(self, value: Any) -> bool:
        return (
            isinstance(value, ForwardedSubscriptionRequest) and
            self.host == value.host and
            self.user == value.user and
            self.client_id == value.client_id and
            self.topic == value.topic and
            self.count == value.count
        )


class NotificationRequest(Message):
    """A notification request message"""

    def __init__(self, topic_pattern: str, is_add: bool) -> None:
        """A request for notification of subscriptions on a topic_pattern.

        Args:
            topic_pattern (str): The topic pattern.
            is_add (bool): True to add a subscription, false to remove.
        """
        super().__init__(MessageType.NOTIFICATION_REQUEST)
        self.topic_pattern = topic_pattern
        self.is_add = is_add

    @classmethod
    def read_body(cls, reader: DataReader) -> NotificationRequest:
        topic_pattern = reader.read_string()
        is_add = reader.read_boolean()
        return NotificationRequest(topic_pattern, is_add)

    def write_body(self, writer: DataWriter) -> None:
        writer.write_string(self.topic_pattern)
        writer.write_boolean(self.is_add)

    def __repr__(self) -> str:
        return f'NotificationRequest({self.topic_pattern!r},{self.is_add!r})'

    def __str__(self) -> str:
        return f'{self.topic_pattern=},{self.is_add=}'

    def __eq__(self, value):
        return (
            isinstance(value, NotificationRequest) and
            self.topic_pattern == value.topic_pattern and
            self.is_add == value.is_add
        )


class SubscriptionRequest(Message):
    """A subscription request message"""

    def __init__(self, topic: str, is_add: bool) -> None:
        """Request a subscription.

        Args:
            topic (str): The topic name.
            is_add (bool): True to add a subscription, False to remove.
        """
        super().__init__(MessageType.SUBSCRIPTION_REQUEST)
        self.topic = topic
        self.is_add = is_add

    @classmethod
    def read_body(cls, reader: DataReader) -> Message:
        topic = reader.read_string()
        is_add = reader.read_boolean()
        return SubscriptionRequest(topic, is_add)

    def write_body(self, writer: DataWriter) -> None:
        writer.write_string(self.topic)
        writer.write_boolean(self.is_add)

    def __repr__(self) -> str:
        return f'SubscriptionRequest({self.topic!r},{self.is_add!r})'

    def __str__(self) -> str:
        return f'{self.topic=},{self.is_add=}'

    def __eq__(self, value: Any) -> bool:
        return (
            isinstance(value, SubscriptionRequest) and
            self.topic == value.topic and
            self.is_add == value.is_add
        )


class ForwardedMulticastData(Message):
    """A forwarded multicast data message"""

    def __init__(
            self,
            host: str,
            user: str,
            topic: str,
            data_packets: list[DataPacket]
    ) -> None:
        """Forwarded multicast data.

        Args:
            host (str): The host from which the data was sent.
            user (str): The user that sent the data.
            topic (str): The topic name.
            data_packets (list[DataPacket]): The data packets.
        """
        super().__init__(MessageType.FORWARDED_MULTICAST_DATA)
        self.host = host
        self.user = user
        self.topic = topic
        self.data_packets = data_packets

    @classmethod
    def read_body(cls, reader: DataReader) -> Message:
        host = reader.read_string()
        user = reader.read_string()
        topic = reader.read_string()
        data_packets = reader.read_data_packet_array()
        return ForwardedMulticastData(host, user, topic, data_packets)

    def write_body(self, writer: DataWriter) -> None:
        writer.write_string(self.host)
        writer.write_string(self.user)
        writer.write_string(self.topic)
        writer.write_data_packet_array(self.data_packets)

    def __repr__(self):
        # pylint: disable=line-too-long
        return f'ForwardedMulticastData({self.host!r},{self.user!r},{self.topic!r},{self.data_packets!r})'

    def __str__(self) -> str:
        # pylint: disable=line-too-long
        return f'{self.host=},{self.user=},{self.topic=},{self.data_packets=}'

    def __eq__(self, value: Any) -> bool:
        return (
            isinstance(value, ForwardedMulticastData) and
            self.host == value.host and
            self.user == value.user and
            self.topic == value.topic and
            self.data_packets == value.data_packets
        )


class ForwardedUnicastData(Message):
    """A forwarded unicast message"""

    def __init__(
            self,
            host: str,
            user: str,
            client_id: str,
            topic: str,
            data_packets: list[DataPacket]
    ) -> None:
        """A forwarded unicast message

        Args:
            host (str): The host from which the message was sent.
            user (str): The user that sent the message.
            client_id (str): The client that sent the message.
            topic (str): The topic name.
            data_packets (list[DataPacket]): The data packets.
        """
        super().__init__(MessageType.FORWARDED_UNICAST_DATA)
        self.host = host
        self.user = user
        self.client_id = client_id
        self.topic = topic
        self.data_packets = data_packets

    @classmethod
    def read_body(cls, reader: DataReader) -> Message:
        host = reader.read_string()
        user = reader.read_string()
        client_id = reader.read_string()
        topic = reader.read_string()
        data_packets = reader.read_data_packet_array()
        return ForwardedUnicastData(host, user, client_id, topic, data_packets)

    def write_body(self, writer: DataWriter) -> None:
        writer.write_string(self.host)
        writer.write_string(self.user)
        writer.write_string(self.client_id)
        writer.write_string(self.topic)
        writer.write_data_packet_array(self.data_packets)

    def __repr__(self) -> str:
        # pylint: disable=line-too-long
        return f'ForwardedUnicastData({self.host!r},{self.user!r},{self.client_id!r},{self.topic!r},{self.data_packets!r})'

    def __str__(self) -> str:
        # pylint: disable=line-too-long
        return f'{self.host=},{self.user=},{self.client_id=},{self.topic=},{self.data_packets=}'

    def __eq__(self, value: Any) -> bool:
        return (
            isinstance(value, ForwardedUnicastData) and
            self.host == value.host and
            self.user == value.user and
            self.client_id == value.client_id and
            self.topic == value.topic and
            self.data_packets == value.data_packets
        )
