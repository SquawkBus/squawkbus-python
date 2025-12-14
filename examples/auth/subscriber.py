"""Authenticated Subscriber"""

import asyncio

from aioconsole import aprint, ainput

from squawkbus import SocketClient, DataPacket


async def on_data(
        sender: str,
        host: str,
        topic: str,
        data: list[DataPacket]
) -> None:
    await aprint(f'{sender=},{host=},{topic=},{data=}')


async def main_async(host: str, port: int) -> None:
    """Start the demo"""

    print("authenticated subscriber")

    print('Enter a username and password.')
    print('Known users are:')
    print('  username="tom", password="tom", roles=Subscribe')
    print('  username="dick", password="dick", roles=Subscribe')
    print('  username="harry", password="harry", roles=Notify|Publish')

    username = input('Username: ')
    password = input('Password: ')
    credentials = (username, password)

    client = await SocketClient.create(host, port, credentials=credentials)
    await aprint(f"Connected as {client.client_id}")
    client.data_handlers.append(on_data)

    topic = await ainput('Topic: ')
    await client.add_subscription(topic)

    await client.wait_closed()


if __name__ == '__main__':
    try:
        asyncio.run(main_async('localhost', 8558))
    except KeyboardInterrupt:
        pass
