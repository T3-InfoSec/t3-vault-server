
from app.services.connection_manager import ConnectionManager
from sqlalchemy.orm import Session


async def handle_complaint(client_id: str, connection_manager: ConnectionManager, data: dict,db:Session):
    # Handle complaint logic here
    await connection_manager.send_to_client(client_id, {"type": "complaintResponse", "data": "{}"})
