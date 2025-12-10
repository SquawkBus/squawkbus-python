"""DataReader"""

import struct

from .data_packet import DataPacket

EMPTY = memoryview(b'')


class DataReader:
    """A data reader class"""

    def __init__(self, buf: bytes) -> None:
        self.buf = memoryview(buf)
        self.offset = 0

    def _read(self, count: int) -> memoryview:
        if count == 0:
            return EMPTY
        start, self.offset = self.offset, self.offset+count
        return self.buf[start:self.offset]

    def read_boolean(self) -> bool:
        """Read a boolean.

        Returns:
            bool: The boolean.
        """
        return self.read_byte() == 1

    def read_byte(self) -> int:
        """Read a byte.

        Returns:
            int: The byte.
        """
        buf = self._read(1)
        return struct.unpack('b', buf)[0]

    def read_int(self) -> int:
        """Read an int.

        Returns:
            int: The int.
        """
        buf = self._read(4)
        return struct.unpack('>i', buf)[0]

    def read_unsigned_int(self) -> int:
        """Read an unsigned int.

        Returns:
            int: The unsigned int.
        """
        buf = self._read(4)
        return struct.unpack('>I', buf)[0]

    def read_string(self, encoding: str = 'utf-8') -> str:
        """Read a string.

        Args:
            encoding (str, optional): The encoding. Defaults to 'utf-8'.

        Returns:
            str: The string.
        """
        buf = self.read_byte_array()
        return buf.decode(encoding)

    def read_byte_array(self) -> bytes:
        """Read an array of bytes.

        Returns:
            Optional[bytes]: The bytes or None.
        """
        count = self.read_int()
        buf = bytes(self._read(count))
        return buf

    def read_int_set(self) -> set[int]:
        """Read a set of ints

        Returns:
            set[int]: The set of ints.
        """
        count = self.read_int()
        return {
            self.read_int()
            for _ in range(count)
        }

    def read_data_packet(self) -> DataPacket:
        """Read a data packet

        Returns:
            DataPacket: The data packet.
        """
        entitlements = self.read_int_set()
        content_type = self.read_string()
        data = self.read_byte_array()
        return DataPacket(entitlements, content_type, data)

    def read_data_packet_array(self) -> list[DataPacket]:
        """Read an array of data packets.

        Returns:
            Optional[List[DataPacket]]: The data packets or None.
        """
        count = self.read_int()
        packets: list[DataPacket] = list()
        for _ in range(count):
            packet = self.read_data_packet()
            packets.append(packet)
        return packets
