import asyncio

from squawkbus import SocketClient, DataPacket


async def main_async(host: str, port: int):

    client = await SocketClient.create(host, port)
    print(f"Connected as {client.client_id}")
    await client.publish(
        "PUB.EXAMPLE",
        [
            DataPacket(
                {0},
                {b'content-type': b'text/plain'},
                b'Hello, World!'
            )
        ]
    )

    client.close()
    await client.wait_closed()

asyncio.run(main_async('localhost', 8558))
