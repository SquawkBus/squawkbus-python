"""DataPacket"""


class DataPacket:
    """A data packet"""

    def __init__(
            self,
            name: str,
            entitlement: int,
            content_type: str,
            data: bytes
    ) -> None:
        """Initialise a data packet.

        Args:
            name (str): The name of the packet.
            entitlement (int): The required packet entitlement.
            content_type (str): The content type of the data.
            data (bytes): The data.
        """
        self.name = name
        self.entitlement = entitlement
        self.content_type = content_type
        self.data = data

    def __str__(self) -> str:
        return f'name={self.name!r},entitlement={self.entitlement},content_type={self.content_type!r}, data={self.data!r}'

    def __repr__(self):
        return f'DataPacket({self.name!r},{self.entitlement}, {self.content_type!r}, {self.data!r})'

    def __eq__(self, value):
        return (
            isinstance(value, DataPacket) and
            self.name == value.name and
            self.entitlement == value.entitlement and
            self.content_type == value.content_type and
            self.data == value.data
        )
