# Dispatch dictionary
from app.models.message_type import MessageType
from app.services.message_handlers.complaints_handelr import handle_complaint
from app.services.message_handlers.exit_handler import handle_exit
from app.services.message_handlers.ping_handler import handle_ping
from app.services.message_handlers.tlp_handler import handle_tlp_task_creation


MESSAGE_TYPE_HANDLERS = {
    MessageType.PING: handle_ping,
    MessageType.TLP: handle_tlp_task_creation,
    MessageType.COMPLAINT: handle_complaint,
    MessageType.EXIT: handle_exit,
}
