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


async def main(host: str, port: int, ssl: bool | SSLContext | None) -> None:
    topic = input('Topic: ')

    client = await SquawkbusClient.create(host, port, ssl=ssl)
    client.data_handlers.append(on_data)

    await client.add_subscription(topic)

    await client.wait_closed()


if __name__ == '__main__':
    try:
        fqdn = socket.getfqdn()
        asyncio.run(main(fqdn, 8558, True))
    except KeyboardInterrupt:
        pass
