"""Authenticated notification subscriber"""

import asyncio

from squawkbus import SquawkbusClient


async def on_notification(
        client_id: str,
        user: str,
        host: str,
        topic: str,
        is_add: bool
) -> None:
    """Handle a notification"""
    print(
        f"on_notification: client_id={client_id!r},user={user!r},host={host!r},topic={topic!r},is_add={is_add}"
    )


async def main_async(host: str, port: int) -> None:
    """Start the demo"""
    print("authenticated notifier")

    print('Enter a username and password.')
    print('Known users are:')
    print('  username="tom", password="tom", roles=Subscribe')
    print('  username="dick", password="dick", roles=Subscribe')
    print('  username="harry", password="harry", roles=Notify|Publish')

    username = input('Username: ')
    password = input('Password: ')
    credentials = (username, password)

    topic = input('Topic: ')

    client = await SquawkbusClient.create(host, port, credentials=credentials)
    client.notification_handlers.append(on_notification)

    await client.add_notification(topic)

    await client.wait_closed()


if __name__ == '__main__':
    try:
        asyncio.run(main_async('localhost', 8558))
    except KeyboardInterrupt:
        pass