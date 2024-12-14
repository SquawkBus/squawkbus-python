"""Authenticated publisher"""

import asyncio
import logging

from aioconsole import ainput, aprint
import click

from squawkbus import SquawkbusClient, DataPacket


async def get_message() -> tuple[str, list[DataPacket]]:
    data_packets: list[DataPacket] = []

    topic = await ainput('Topic: ')

    ok = topic != ''
    while ok:
        entitlement = await ainput("Entitlement (<ENTER> to stop): ")
        if entitlement == '':
            ok = False
            continue

        content_type = await ainput("Content type (text/plain): ")
        if content_type == '':
            content_type = 'text/plain'

        data = await ainput("Data: ")

        packet = DataPacket(
            int(entitlement),
            content_type,
            data.encode('utf-8')
        )
        data_packets.append(packet)

    return topic, data_packets


async def main_async(host: str, port: int) -> None:
    print('Enter a username and password.')
    print('Known users are:')
    print('  username="tom", password="tom", roles=Subscribe')
    print('  username="dick", password="dick", roles=Subscribe')
    print('  username="harry", password="harry", roles=Notify|Publish')

    username = input('Username: ')
    password = input('Password: ')
    credentials = (username, password)

    client = await SquawkbusClient.create(host, port, credentials=credentials)

    while True:
        await aprint("Enter a new message")
        topic, data_packets = await get_message()
        if not topic:
            break

        await client.publish(topic, data_packets)

    client.close()
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
