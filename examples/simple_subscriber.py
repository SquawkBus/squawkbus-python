"""Simple subscriber"""

import asyncio
import logging

import click

from squawkbus import SquawkbusClient, DataPacket

LOG = logging.getLogger("subscriber")


async def on_data(
        sender: str,
        host: str,
        topic: str,
        data: list[DataPacket]
) -> None:
    print(f'sender="{sender}",host="{host}",topic="{topic}",data={data}')


async def main_async(host: str, port: int):
    topic = input('Topic: ')

    client = await SquawkbusClient.create(host, port)
    client.data_handlers.append(on_data)

    await client.add_subscription(topic)

    await client.wait_closed()


@click.command()
@click.option("-h", "--host", "host", type=str, default="localhost")
@click.option("-p", "--port", "port", type=int, default=8558)
def main(host: str, port: int) -> None:
    logging.basicConfig(level=logging.ERROR)
    asyncio.run(main_async(host, port))


if __name__ == '__main__':
    # pylint: disable=no-value-for-parameter
    main()
