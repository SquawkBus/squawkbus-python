"""Authenticated publisher"""

import asyncio
import socket

from aioconsole import ainput, aprint

from squawkbus import SquawkbusClient, DataPacket


async def read_console() -> list[DataPacket]:
    """Read the data packets"""
    await aprint('Enter an empty message finish the data packet. Entitlements can be empty')
    await aprint('or a comma separated list of ints, e.g.: 1, 2, 3')
    data_packets: list[DataPacket] = list()
    while True:
        entitlement = await ainput('Entitlement: ')
        if not entitlement:
            break
        content_type = await ainput('Content Type: ')
        if not content_type:
            break
        message = await ainput('Message: ')
        if not message:
            break
        data_packet = DataPacket(
            int(entitlement),
            content_type,
            message.encode('utf8')
        )
        data_packets.append(data_packet)
    return data_packets


async def main(host: str):
    print("authenticated publisher")

    print('Enter a username and password.')
    print('Known users are:')
    print('  username="tom", password="tom", roles=Subscribe')
    print('  username="dick", password="dick", roles=Subscribe')
    print('  username="harry", password="harry", roles=Notify|Publish')

    username = input('Username: ')
    password = input('Password: ')

    topic = input('Topic: ')

    client = await SquawkbusClient.create(
        host,
        8558,
        ssl=True,
        credentials=(username, password)
    )

    print('starting the client')
    console_task = asyncio.create_task(read_console())
    client_task = asyncio.create_task(client.start())
    pending = {
        client_task,
        console_task
    }

    while pending:

        done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)

        for task in done:
            if task == client_task:
                break
            elif task == console_task:
                data_packets = console_task.result()
                if not data_packets:
                    client.stop()
                else:
                    print(
                        f'Publishing to topic "{topic}" the data packets "{data_packets}"'
                    )
                    await client.publish(topic, data_packets)
                    console_task = asyncio.create_task(read_console())
                    pending.add(console_task)

if __name__ == '__main__':
    fqdn = socket.getfqdn()
    asyncio.run(main(fqdn))
