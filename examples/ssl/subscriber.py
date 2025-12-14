"""Simple subscriber"""

import asyncio
import socket
from ssl import SSLContext

from aioconsole import ainput, aprint

from squawkbus import SocketClient, DataPacket


async def on_data(
        sender: str,
        host: str,
        topic: str,
        data: list[DataPacket]
) -> None:
    await aprint(f'{sender=},{host=},{topic=},{data=}')


async def main(host: str, port: int, ssl: bool | str | SSLContext | None) -> None:

    client = await SocketClient.create(host, port, ssl=ssl)
    await aprint(f"Connected as {client.client_id}")

    client.data_handlers.append(on_data)

    topic = await ainput('Topic: ')
    await client.add_subscription(topic)

    await client.wait_closed()


if __name__ == '__main__':
    try:
        HOST = socket.getfqdn()
        PORT = 8558
        SSL = True
        # import os
        # SSL = os.path.expanduser("~/.keys/cacerts.pem")
        asyncio.run(main(HOST, PORT, SSL))
    except KeyboardInterrupt:
        pass
