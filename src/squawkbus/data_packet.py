"""DataPacket"""


class DataPacket:
    """A data packet"""

    def __init__(
            self,
            entitlement: int,
            content_type: str,
            data: bytes
    ) -> None:
        """Initialise a data packet.

        Args:
            entitlement (int): The required packet entitlement.
            content_type (str): The content type of the data.
            data (bytes): The data.
        """
        self.entitlement = entitlement
        self.content_type = content_type
        self.data = data

    def __str__(self) -> str:
        return f'entitlement={self.entitlement},content_type={self.content_type!r}, data={self.data!r}'

    def __repr__(self):
        return f'DataPacket({self.entitlement}, {self.content_type!r}, {self.data!r})'

    def __eq__(self, value):
        return (
            isinstance(value, DataPacket) and
            self.entitlement == value.entitlement and
            self.content_type == value.content_type and
            self.data == value.data
        )
