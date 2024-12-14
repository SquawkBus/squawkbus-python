"""Authenticated Subscriber"""

import asyncio
import logging

import click

from squawkbus import SquawkbusClient, DataPacket


async def on_data(
        sender: str,
        host: str,
        topic: str,
        data: list[DataPacket]
) -> None:
    print(f'sender="{sender}",host="{host}",topic="{topic}",data={data}')


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

    topic = input('Topic: ')

    client = await SquawkbusClient.create(host, port, credentials=credentials)
    client.data_handlers.append(on_data)

    await client.add_subscription(topic)

    await client.wait_closed()


@click.command()
@click.option("-h", "--host", "host", type=str, default='localhost')
@click.option("-p", "--port", "port", type=int, default=8558)
def main(host: str, port: int) -> None:
    try:
        logging.basicConfig(level=logging.ERROR)
        asyncio.run(main_async(host, port))
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    # pylint: disable=no-value-for-parameter
    main()
