"""Test Serialization"""

from asyncio import IncompleteReadError, StreamReader, StreamWriter
import pytest

from squawkbus.frame_stream import FrameStream

# from tests.mock_streams import MockStreamReader, MockStreamWriter


class MockStreamReader(StreamReader):

    def __init__(self, buf: bytearray) -> None:
        self._buf = buf
        self._offset = 0

    async def readexactly(self, n: int) -> bytes:
        start, self._offset = self._offset, self._offset + n
        if self._offset > len(self._buf):
            raise IncompleteReadError(self._buf[start:], n)
        return bytes(self._buf[start:self._offset])


class MockStreamWriter(StreamWriter):

    def __init__(self, buf: bytearray) -> None:
        self._buf = buf

    def write(self, data: bytes) -> None:
        """Write data to the stream."""
        self._buf += data

    async def drain(self) -> None:
        pass


@pytest.mark.asyncio
async def test_roundtrip():
    """Test round trip serialization"""

    buf = bytearray()
    reader, writer = MockStreamReader(buf), MockStreamWriter(buf)
    frame_stream = FrameStream(reader, writer)
    buf_in = b'This is not a test'
    await frame_stream.write(buf_in)
    buf_out = await frame_stream.read()
    assert buf_in == buf_out
