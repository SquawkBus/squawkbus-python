"""DataPacket"""


class DataPacket:
    """A data packet"""

    def __init__(
            self,
            entitlements: set[int],
            content_type: str,
            data: bytes
    ) -> None:
        """Initialise a data packet.

        Args:
            entitlements (set[int]): The required packet entitlements.
            content_type (str): The content type of the data.
            data (bytes): The data.
        """
        self.entitlements = entitlements
        self.content_type = content_type
        self.data = data

    def __str__(self) -> str:
        return f'{self.entitlements=},{self.content_type=},{self.data=}'

    def __repr__(self):
        return f'DataPacket({self.entitlements!r},{self.content_type!r},{self.data!r})'

    def __eq__(self, value):
        return (
            isinstance(value, DataPacket) and
            self.entitlements == value.entitlements and
            self.content_type == value.content_type and
            self.data == value.data
        )
