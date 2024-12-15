"""Simple subscriber"""

import asyncio
import socket
from ssl import SSLContext

from squawkbus import SquawkbusClient, DataPacket


async def on_data(
        sender: str,
        host: str,
        topic: str,
        data: list[DataPacket]
) -> None:
    print(f'sender="{sender}",host="{host}",topic="{topic}",data={data}')


async def main(host: str, port: int, ssl: bool | str | SSLContext | None) -> None:
    topic = input('Topic: ')

    client = await SquawkbusClient.create(host, port, ssl=ssl)
    client.data_handlers.append(on_data)

    await client.add_subscription(topic)

    await client.wait_closed()


if __name__ == '__main__':
    try:
        HOST = socket.getfqdn()
        PORT = 8558
        SSL = True
        asyncio.run(main(HOST, PORT, SSL))
    except KeyboardInterrupt:
        pass
