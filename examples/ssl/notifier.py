"""Simple Notifier"""

import asyncio
import socket
from ssl import SSLContext

from squawkbus import SquawkbusClient


async def on_notification(
        client_id: str,
        user: str,
        host: str,
        topic: str,
        is_add: bool
) -> None:
    print(
        f"client_id={client_id},user='{user}',host='{host}',topic='{topic}',is_add={is_add}"
    )


async def main(host: str, port: int, ssl: bool | str | SSLContext | None) -> None:
    topic_pattern = input('Topic pattern: ')

    client = await SquawkbusClient.create(host, port, ssl=ssl)
    client.notification_handlers.append(on_notification)

    await client.add_notification(topic_pattern)

    await client.wait_closed()


if __name__ == '__main__':
    try:
        HOST = socket.getfqdn()
        PORT = 8558
        SSL = True
        asyncio.run(main(HOST, PORT, SSL))
    except KeyboardInterrupt:
        pass
