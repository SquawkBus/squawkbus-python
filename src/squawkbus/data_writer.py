"""DataWriter"""

from __future__ import annotations

import struct

from .data_packet import DataPacket


class DataWriter:
    """Data Writer"""

    def __init__(self) -> None:
        self.buf = bytearray()

    def write_boolean(self, val: bool) -> DataWriter:
        """Write a boolean

        Args:
            val (bool): Th boolean value.
        """
        self.write_byte(1 if val else 0)
        return self

    def write_byte(self, val: int) -> DataWriter:
        """Write a byte

        Args:
            val (int): The value to write.
        """
        self.buf += struct.pack('b', val)
        return self

    def write_int(self, val) -> DataWriter:
        """Write an int

        Args:
            val ([type]): The int value.
        """
        self.buf += struct.pack('>i', val)
        return self

    def write_string(self, val: str, encoding: str = 'utf-8') -> DataWriter:
        """Writ a string.

        Args:
            val (str): The string to write.
            encoding (str, optional): The encoding. Defaults to 'utf-8'.
        """
        buf = val.encode(encoding)
        return self.write_byte_array(buf)

    def write_byte_array(self, val: bytes) -> DataWriter:
        """Write an array of bytes.

        Args:
            val (Optional[bytes]): The bytes to write.
        """
        self.write_int(len(val))
        if len(val) > 0:
            self.buf += val
        return self

    def write_data_packet(self, val: DataPacket) -> DataWriter:
        """Write a data packet.

        Args:
            val (DataPacket): The data packets.
        """
        self.write_int(val.entitlement)
        self.write_string(val.content_type)
        self.write_byte_array(val.data)
        return self

    def write_data_packet_array(self, val: list[DataPacket]) -> DataWriter:
        """Write an array of data packets.

        Args:
            val (list[DataPacket]): The data packets or None.
        """
        self.write_int(len(val))
        for packet in val:
            self.write_data_packet(packet)
        return self
