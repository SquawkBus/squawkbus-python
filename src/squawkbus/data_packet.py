"""DataPacket"""


class DataPacket:
    """A data packet"""

    def __init__(
            self,
            entitlements: set[int],
            headers: dict[bytes, bytes],
            data: bytes
    ) -> None:
        """Initialise a data packet.

        Args:
            entitlements (set[int]): The required packet entitlements.
            headers (dict[bytes, bytes]): The headers.
            data (bytes): The data.
        """
        self.entitlements = entitlements
        self.headers = headers
        self.data = data

    def __str__(self) -> str:
        return f'{self.entitlements=},{self.headers=},{self.data=}'

    def __repr__(self):
        return f'DataPacket({self.entitlements!r},{self.headers!r},{self.data!r})'

    def __eq__(self, value):
        return (
            isinstance(value, DataPacket) and
            self.entitlements == value.entitlements and
            self.headers == value.headers and
            self.data == value.data
        )
