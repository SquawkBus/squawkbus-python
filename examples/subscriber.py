"""Callback Subscriber"""

import asyncio
import json
import logging

from aioconsole import ainput
from squawkbus import SquawkbusClient, DataPacket

LOG = logging.getLogger("subscriber")


async def on_data(
        user: str,
        host: str,
        topic: str,
        data_packets: list[DataPacket]
) -> None:
    """Handle a data message"""
    LOG.info('data: user="%s",host="%s",topic="%s"', user, host, topic)

    if not data_packets:
        LOG.debug("no data")
        return

    for packet in data_packets:

        LOG.debug('packet entitlement=%s', packet.entitlement)

        LOG.debug('unpacking data with content_type="%s"', packet.content_type)
        if packet.content_type == "text/plain":
            data = packet.data.decode('utf8')
        elif packet.content_type == "application/json":
            data = json.loads(packet.data)
        else:
            LOG.debug("unhandled content type")
            continue

        LOG.debug("data: %s", data)


async def main():
    """Start the demo"""
    print('Example subscriber')

    client = await SquawkbusClient.create('localhost', 8558)
    client.data_handlers.append(on_data)

    topic = await ainput('Topic: ')
    LOG.info("Subscribing to topic '%s'", topic)
    await client.add_subscription(topic)

    await client.start()

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(main())
