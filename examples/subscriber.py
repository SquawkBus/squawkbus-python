"""Simple subscriber"""

import asyncio
import logging

from squawkbus import SquawkbusClient, DataPacket

LOG = logging.getLogger("subscriber")


async def on_data(
        sender: str,
        host: str,
        topic: str,
        data: list[DataPacket]
) -> None:
    print(f'sender="{sender}",host="{host}",topic="{topic}",data={data}')


async def main():
    topic = input('Topic: ')

    client = await SquawkbusClient.create('localhost', 8558)
    client.data_handlers.append(on_data)

    await client.add_subscription(topic)

    await client.wait_closed()

if __name__ == '__main__':
    logging.basicConfig(level=logging.ERROR)
    asyncio.run(main())
