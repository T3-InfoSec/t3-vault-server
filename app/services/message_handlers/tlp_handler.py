
from app.services.connection_manager import ConnectionManager
from sqlalchemy.orm import Session


async def handle_tlp(client_id: str, connection_manager: ConnectionManager, data: dict,db:Session):
    # Handle TLP logic here
    await connection_manager.send_to_client(client_id, {"type": "tlpResult", "data": "{}"})
