# Dispatch dictionary
from app.models.message_type import MessageSolverResponseType, MessageType
from app.services.message_handlers.complaints_handelr import handle_complaint
from app.services.message_handlers.exit_handler import handle_exit
from app.services.message_handlers.handle_solver_status_update import handle_solver_status_update
from app.services.message_handlers.handle_solver_tlp_reponse import handle_solver_tlp_reponse
from app.services.message_handlers.ping_handler import handle_ping_cient, handle_ping_solver
from app.services.message_handlers.tlp_handler import handle_tlp_task_creation


MESSAGE_TYPE_HANDLERS = {
    MessageType.PING: handle_ping_cient,
    MessageType.TLP: handle_tlp_task_creation,
    MessageType.COMPLAINT: handle_complaint,
    MessageType.EXIT: handle_exit,    
    # Add more handlers as needed
}

MESSAGE_SOLVER_RESPONSE_TYPE_HANDLERS = {
    MessageSolverResponseType.TLP_RESPONSE: handle_solver_tlp_reponse,
    MessageSolverResponseType.STATUS_UPDATE: handle_solver_status_update,    
    MessageSolverResponseType.PING: handle_ping_solver,
    # Add more handlers as needed
}