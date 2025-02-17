"""Tests for messages"""

from base64 import b64encode

from squawkbus.data_packet import DataPacket
from squawkbus.messages import (
    Message,
    MulticastData,
    UnicastData,
    ForwardedSubscriptionRequest,
    NotificationRequest,
    SubscriptionRequest,
    AuthenticationRequest,
    AuthenticationResponse,
    ForwardedMulticastData,
    ForwardedUnicastData
)


def test_multicast_data():
    """Test multicast data message"""
    source = MulticastData(
        'topic',
        [
            DataPacket('', 1, 'text/plain', b'first'),
            DataPacket('', 0, 'text/plain', b'second'),
        ]
    )
    dest = Message.deserialize(source.serialize())
    assert source == dest


def test_unicast_data():
    """Test unicast data message"""
    source = UnicastData(
        '12345678123456781234567812345678',
        'topic',
        [
            DataPacket('', 1, 'text/plain', b'first'),
            DataPacket('', 0, 'text/plain', b'second'),
        ]
    )
    dest = Message.deserialize(source.serialize())
    assert source == dest


def test_forwarded_subscription_request():
    """Test forwarded subscription request"""
    source = ForwardedSubscriptionRequest(
        'user',
        'host',
        '12345678123456781234567812345678',
        'topic',
        True
    )
    dest = Message.deserialize(source.serialize())
    assert source == dest


def test_notification_request():
    """Test notification request"""
    source = NotificationRequest(
        '.*\\.LSE',
        True
    )
    dest = Message.deserialize(source.serialize())
    assert source == dest


def test_subscription_request():
    """Test subscription request"""
    source = SubscriptionRequest(
        'topic',
        True
    )
    dest = Message.deserialize(source.serialize())
    assert source == dest


def test_authentication_request():
    """Test authentication request"""
    source = AuthenticationRequest(
        'basic',
        b64encode(b'aladdin:opensesame')
    )
    dest = Message.deserialize(source.serialize())
    assert source == dest


def test_authentication_response():
    """Test authentication response"""
    source = AuthenticationResponse(
        'xxxx'
    )
    dest = Message.deserialize(source.serialize())
    assert source == dest


def test_forwarded_multicast_data():
    """Test forwarded multicast data message"""
    source = ForwardedMulticastData(
        'user',
        'host',
        'topic',
        [
            DataPacket('', 1, 'text/plain', b'first'),
            DataPacket('', 0, 'text/plain', b'second'),
        ]
    )
    dest = Message.deserialize(source.serialize())
    assert source == dest


def test_forwarded_unicast_data():
    """Test forwarded unicast data message"""
    source = ForwardedUnicastData(
        'user',
        'host',
        '12345678123456781234567812345678',
        'topic',
        [
            DataPacket('', 1, 'text/plain', b'first'),
            DataPacket('', 0, 'text/plain', b'second'),
        ]
    )
    dest = Message.deserialize(source.serialize())
    assert source == dest
