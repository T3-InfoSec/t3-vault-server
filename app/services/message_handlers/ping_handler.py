
from app.services.connection_manager import ConnectionManager
from sqlalchemy.orm import Session


async def handle_ping(client_id: str, connection_manager: ConnectionManager,db:Session):
    await connection_manager.send_to_client(client_id, {"type": "pong", "data": "{}"})
