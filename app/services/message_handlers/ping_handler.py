from app.models.message_type import MessageResponseType
from app.services.connection_manager import ConnectionManager
from sqlalchemy.orm import Session


async def handle_ping_cient(
    client_id: str, connection_manager: ConnectionManager, db: Session
):

    await connection_manager.send_to_client(
        client_id,
        {"type": f"{MessageResponseType.PONG.value}", "data": "{}"},
    )

async def handle_ping_solver(
    solver_id: str, connection_manager: ConnectionManager, db: Session,data: dict
):
    await connection_manager.send_to_solver(
        solver_id,
        {"type": f"{MessageResponseType.PONG.value}", "data": "{}"},
    )
