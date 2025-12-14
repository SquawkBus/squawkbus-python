"""Simple Notifier"""

import asyncio
import logging

from aioconsole import aprint, ainput

from squawkbus import SocketClient


async def on_notification(
        client_id: str,
        user: str,
        host: str,
        topic: str,
        count: int
) -> None:
    await aprint(f"{client_id=},{user=},{host=},{topic=},{count=}")


async def main_async(host: str, port: int):

    client = await SocketClient.create(host, port)
    await aprint(f"Connected as {client.client_id}")
    client.notification_handlers.append(on_notification)

    topic_pattern = await ainput('Topic pattern: ')
    await client.add_notification(topic_pattern)

    await client.wait_closed()


if __name__ == '__main__':
    logging.basicConfig(level=logging.WARNING)
    try:
        asyncio.run(main_async('localhost', 8558))
    except KeyboardInterrupt:
        pass
