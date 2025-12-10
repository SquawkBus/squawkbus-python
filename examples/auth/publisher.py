"""Authenticated publisher"""

import asyncio

from aioconsole import ainput, aprint

from squawkbus import SocketClient, DataPacket


async def get_message() -> tuple[str, list[DataPacket]]:
    data_packets: list[DataPacket] = []

    topic = await ainput('Topic: ')

    ok = topic != ''
    while ok:
        data = await ainput("Data (<ENTER> to stop): ")
        if data == '':
            ok = False
            continue

        text = await ainput("Entitlements (0): ")
        if text == '':
            text = "0"
        entitlements = {int(i.strip()) for i in text.split(',')}

        text = await ainput("Headers (content-type:text/plain): ")
        if text == '':
            text = 'content-type:text/plain'
        headers = {
            key.strip().encode(): value.strip().encode()
            for item in text.split(',')
            for key, value in [item.strip().split(':', 1)]
        }

        packet = DataPacket(
            entitlements,
            headers,
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

    client = await SocketClient.create(host, port, credentials=credentials)
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
        asyncio.run(main_async('localhost', 8558))
    except KeyboardInterrupt:
        pass
