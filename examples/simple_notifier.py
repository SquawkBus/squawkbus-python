"""Notification Subscriber"""

import asyncio

from aioconsole import ainput, aprint

from squawkbus import SquawkbusClient


async def on_notification(
        client_id: str,
        user: str,
        host: str,
        topic: str,
        is_add: bool
) -> None:
    print(
        f"client_id={client_id},user='{user}',host='{host}',topic='{topic}'',is_add={is_add}"
    )


async def main():
    topic_pattern = input('Topic pattern: ')

    client = await SquawkbusClient.create('localhost', 8558)
    client.notification_handlers.append(on_notification)
    
    await aprint(f"Requesting notification of subscriptions on topic pattern '{topic_pattern}'")
    await client.add_notification(topic_pattern)

    await client.wait_closed()

if __name__ == '__main__':
    asyncio.run(main())
