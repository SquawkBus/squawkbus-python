"""Callback Subscriber"""

import asyncio
import json

from squawkbus import SquawkbusClient, DataPacket


async def on_data(
        user: str,
        host: str,
        topic: str,
        data_packets: list[DataPacket]
) -> None:
    """Handle a data message"""
    print(f'data: user="{user}",host="{host}",topic="{topic}"')

    if not data_packets:
        print("no data")
        return

    for packet in data_packets:

        print(f'packet entitlement={packet.entitlement}')

        print(f'unpacking data with content_type={packet.content_type!r}')
        if packet.content_type == "text/plain":
            data = packet.data.decode('utf8')
        elif packet.content_type == "application/json":
            data = json.loads(packet.data)
        else:
            print("unhandled content type")
            continue

        print(data)


async def main():
    """Start the demo"""
    print('Example subscriber')
    topic = input('Topic: ')

    client = await SquawkbusClient.create('localhost', 9001)
    client.data_handlers.append(on_data)

    print(f"Subscribing to topic '{topic}'")
    await client.add_subscription(topic)

    await client.start()

if __name__ == '__main__':
    asyncio.run(main())
