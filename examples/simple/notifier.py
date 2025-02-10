"""Simple Notifier"""

import asyncio
import logging

from aioconsole import aprint

from squawkbus import SocketClient


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


async def main_async(host: str, port: int):
    topic_pattern = input('Topic pattern: ')

    client = await SocketClient.create(host, port)
    await aprint(f"Connected as {client.client_id}")
    client.notification_handlers.append(on_notification)

    await client.add_notification(topic_pattern)

    await client.wait_closed()


if __name__ == '__main__':
    logging.basicConfig(level=logging.WARNING)
    try:
        asyncio.run(main_async('localhost', 8558))
    except KeyboardInterrupt:
        pass
