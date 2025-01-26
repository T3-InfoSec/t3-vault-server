from enum import Enum
class MessageType(Enum):
    PING = "ping"
    TLP = "tlp"
    COMPLAINT = "complaint"
    EXIT = "exit"


class MessageResponseType(Enum):
    PONG = "pong"
    TLP_RESPONSE = "tlpResponse"
    COMPLAINT_RESPONSE = "complaintResponse"
    EXIT_RESPONSE = "exitResponse"

class MessageSolverResponseType(Enum):
    PING = "ping"
    TLP_RESPONSE = "tlpSolverResponse"
    COMPLAINT_RESPONSE = "complaintSolverResponse"
    STATUS_UPDATE = "statusUpdate"