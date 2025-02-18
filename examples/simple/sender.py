"""Simple Publisher"""

import asyncio
import logging

from aioconsole import ainput, aprint

from squawkbus import SocketClient, DataPacket


async def get_message() -> tuple[str, str, list[DataPacket]]:
    data_packets: list[DataPacket] = []

    client_id = await ainput("Client ID: ")
    topic = await ainput('Topic: ')

    ok = topic != '' and client_id != ''
    while ok:
        data = await ainput("Data (<ENTER> to stop): ")
        if data == '':
            ok = False
            continue

        entitlement = await ainput("Entitlement (0): ")
        if entitlement == '':
            entitlement = '0'

        content_type = await ainput("Content type (text/plain): ")
        if content_type == '':
            content_type = 'text/plain'

        packet = DataPacket(
            "message",
            int(entitlement),
            content_type,
            data.encode('utf-8')
        )
        data_packets.append(packet)

    return client_id, topic, data_packets


async def main_async(host: str, port: int):

    client = await SocketClient.create(host, port)
    await aprint(f"Connected as {client.client_id}")

    while True:
        await aprint("Enter a new message")
        client_id, topic, data_packets = await get_message()
        if not topic:
            break

        await client.send(client_id, topic, data_packets)

    client.close()
    await client.wait_closed()


if __name__ == '__main__':
    logging.basicConfig(level=logging.WARNING)
    try:
        asyncio.run(main_async('localhost', 8558))
    except KeyboardInterrupt:
        pass
