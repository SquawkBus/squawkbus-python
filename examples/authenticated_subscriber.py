"""Authenticated Subscriber"""

import asyncio
import socket
import ssl

from squawkbus import SquawkbusClient, DataPacket


async def on_data(
        user: str,
        host: str,
        topic: str,
        data_packets: list[DataPacket]
) -> None:
    """Handle a data message"""
    print(f'data: user="{user}",host="{host}",topic="{topic}"')
    if not data_packets:
        print("no data")
    else:
        for packet in data_packets:
            message = packet.data.decode('utf8') if packet.data else None
            print(
                f'packet: entitlement={packet.entitlement},message={message}')


async def main(host: str) -> None:
    """Start the demo"""

    print("authenticated subscriber")

    print('Enter a username and password.')
    print('Known users are:')
    print('  username="tom", password="tom", roles=Subscribe')
    print('  username="dick", password="dick", roles=Subscribe')
    print('  username="harry", password="harry", roles=Notify|Publish')

    username = input('Username: ')
    password = input('Password: ')

    topic = input('Topic: ')

    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    client = await SquawkbusClient.create(
        host, 9001,
        ssl=ssl_context,
        credentials=(username, password)
    )

    print(f"Subscribing to topic '{topic}'")
    client.data_handlers.append(on_data)
    await client.add_subscription(topic)

    print('Starting the client')
    await client.start()

if __name__ == '__main__':
    fqdn = socket.getfqdn()
    asyncio.run(main(fqdn))
