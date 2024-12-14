"""Notification Subscriber"""

import asyncio
import logging

import click

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


async def main_async(host: str, port: int):
    topic_pattern = input('Topic pattern: ')

    client = await SquawkbusClient.create(host, port)
    client.notification_handlers.append(on_notification)

    await client.add_notification(topic_pattern)

    await client.wait_closed()


@click.command()
@click.option("-h", "--host", "host", type=str, default="localhost")
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
