"""Simple subscriber"""

import asyncio
import logging

from aioconsole import aprint, ainput

from squawkbus import SocketClient, DataPacket


async def on_data(
        sender: str,
        host: str,
        topic: str,
        data: list[DataPacket]
) -> None:
    print(f'sender="{sender}",host="{host}",topic="{topic}",data={data}')


async def main_async(host: str, port: int):

    client = await SocketClient.create(host, port)
    await aprint(f"Connected as {client.client_id}")
    client.data_handlers.append(on_data)

    topic = await ainput('Topic: ')
    await client.add_subscription(topic)

    await client.wait_closed()


if __name__ == '__main__':
    logging.basicConfig(level=logging.WARNING)
    try:
        asyncio.run(main_async('localhost', 8558))
    except KeyboardInterrupt:
        pass
