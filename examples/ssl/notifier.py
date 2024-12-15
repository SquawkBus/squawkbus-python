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


async def main(host: str, port: int, ssl: bool | SSLContext | None) -> None:
    topic_pattern = input('Topic pattern: ')

    client = await SquawkbusClient.create(host, port, ssl=ssl)
    client.notification_handlers.append(on_notification)

    await client.add_notification(topic_pattern)

    await client.wait_closed()


if __name__ == '__main__':
    try:
        fqdn = socket.getfqdn()
        asyncio.run(main(fqdn, 8558, True))
    except KeyboardInterrupt:
        pass
