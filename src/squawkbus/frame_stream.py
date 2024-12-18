"""FrameStream"""

from asyncio import StreamReader, StreamWriter
import struct


class FrameStream:
    """A frame is a buffer that is transmitted as a 4 byte length, followed by
    the bytes."""

    def __init__(self, reader: StreamReader, writer: StreamWriter) -> None:
        self._reader = reader
        self._writer = writer

    async def read(self) -> bytes:
        """Read a frame from the input stream.

        The stream starts with a 4 byte network-order integer, which holds the
        length of the following data.

        Returns:
            bytes: The frame contents.
        """
        buf = await self._reader.readexactly(4)
        (count,) = struct.unpack('>i', buf)
        buf = await self._reader.readexactly(count)
        return buf

    async def write(self, buf: bytes) -> None:
        """Write a frame to the output stream.

        Args:
            buf (bytes): The data to write.
        """
        self._writer.write(struct.pack('>i', len(buf)))
        self._writer.write(buf)
        await self._writer.drain()

    async def close(self) -> None:
        """Close the stream"""
        self._writer.close()
        await self._writer.wait_closed()
