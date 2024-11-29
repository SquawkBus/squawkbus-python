"""Authenticated notification subscriber"""

import asyncio
import socket
import ssl

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


async def main(host: str) -> None:
    """Start the demo"""
    print("authenticated notifier")

    print('Enter a username and password.')
    print('Known users are:')
    print('  username="tom", password="tom", roles=Subscribe')
    print('  username="dick", password="dick", roles=Subscribe')
    print('  username="harry", password="harry", roles=Notify|Publish')

    username = input('Username: ')
    password = input('Password: ')
    topic = input('Topic: ')

    ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    client = await SquawkbusClient.create(
        host,
        8558,
        ssl=ssl_context,
        credentials=(username, password)
    )

    print(f"Requesting notification of subscriptions on topic '{topic}'")
    client.notification_handlers.append(on_notification)
    await client.add_notification(topic)

    print('Starting the client')
    await client.start()

if __name__ == '__main__':
    fqdn = socket.getfqdn()
    asyncio.run(main(fqdn))
