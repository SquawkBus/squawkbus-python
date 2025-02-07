"""Simple Publisher"""

import asyncio
import socket
from ssl import SSLContext

from aioconsole import ainput, aprint

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
            "message",
            int(entitlement),
            content_type,
            data.encode('utf-8')
        )
        data_packets.append(packet)

    return topic, data_packets


async def main(host: str, port: int, ssl: bool | str | SSLContext | None) -> None:

    client = await SquawkbusClient.create(host, port, ssl=ssl)
    await aprint(f"Connected as {client.client_id}")

    while True:
        await aprint("Enter a new message")
        topic, data_packets = await get_message()
        if not topic:
            break

        await client.publish(topic, data_packets)

    client.close()
    await client.wait_closed()


if __name__ == '__main__':
    try:
        HOST = socket.getfqdn()
        PORT = 8558
        SSL = True
        asyncio.run(main(HOST, PORT, SSL))
    except KeyboardInterrupt:
        pass
