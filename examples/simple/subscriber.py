"""Simple subscriber"""

import asyncio

from squawkbus import SquawkbusClient, DataPacket


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


if __name__ == '__main__':
    try:
        asyncio.run(main_async('localhost', 8558))
    except KeyboardInterrupt:
        pass
