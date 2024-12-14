"""Simple Subscriber"""

import asyncio

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
            int(entitlement),
            content_type,
            data.encode('utf-8')
        )
        data_packets.append(packet)

    return topic, data_packets

async def main() -> None:
    await aprint('Example publisher')

    client = await SquawkbusClient.create('localhost', 8558)

    while True:
        topic = await ainput('Topic: ')
        if topic == '':
            break
        data_packets: list[DataPacket] = []
        while True:
            entitlement = await ainput("Entitlement (<ENTER> to stop): ")
            if entitlement == '':
                break
            content_type = await ainput("Content type (text/plain): ")
            if content_type == '':
                content_type = 'text/plain'
            data = await ainput("Data: ")
            packet = DataPacket(int(entitlement), content_type, data.encode('utf-8'))
            data_packets.append(packet)

            await aprint(f"Sending to {topic} data {data_packets}")
            await client.publish(topic, data_packets)
    
    client.close()
    await client.wait_closed()

if __name__ == '__main__':
    asyncio.run(main())
