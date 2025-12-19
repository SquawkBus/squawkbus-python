import asyncio

from squawkbus import SocketClient, DataPacket


async def on_data(
        sender: str,
        host: str,
        topic: str,
        data: list[DataPacket]
) -> None:
    print(f'{sender=},{host=},{topic=},{data=}')


async def main_async(host: str, port: int):

    client = await SocketClient.create(host, port)
    print(f"Connected as {client.client_id}")
    client.data_handlers.append(on_data)

    await client.add_subscription("PUB.EXAMPLE")

    await client.wait_closed()

asyncio.run(main_async('localhost', 8558))
