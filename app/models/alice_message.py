from dataclasses import dataclass
from enum import Enum
from typing import Union

from app.models.alice_tlp_data import AliceTLPData

# Define the MESSAGE_TYPE enum
class MessageType(Enum):
    TLP_MESSAGE = "TLP_MESSAGE"
    HANDSHAKE = "HANDSHAKE"


@dataclass
class HandshakeMessage:    
    data: str

@dataclass
class AliceMessage:
    key: str
    message_type: MessageType
    message: Union[str, AliceTLPData, HandshakeMessage]

    def to_dict(self) -> dict:
        """Convert the AliceMessage instance to a dictionary."""
        return {
            "key": self.key,
            "messageType": self.message_type.value,
            "message": self.message if isinstance(self.message, str) else self.message.__dict__,
        }

    @staticmethod
    def from_dict(data: dict) -> 'AliceMessage':
        """Create an AliceMessage instance from a dictionary."""
        message_type = MessageType(data["messageType"])
        raw_message = data["message"]

        # At this stage, the message is assumed to be a string (encrypted data)
        return AliceMessage(
            key=data["key"],
            message_type=message_type,
            message=raw_message
        )

    def decrypt_and_parse(self, decryption_function) -> None:
        """
        Decrypt and parse the message based on its type.
        
        Args:
            decryption_function (callable): A function that decrypts the message string.
        """
        if isinstance(self.message, str):  # Ensure it's still encrypted data
            decrypted_data = decryption_function(self.message)
            if self.message_type == MessageType.TLP_MESSAGE:
                self.message = AliceTLPData(**decrypted_data)
            elif self.message_type == MessageType.HANDSHAKE:
                self.message = HandshakeMessage(**decrypted_data)
            else:
                raise ValueError("Invalid message type for decryption")
