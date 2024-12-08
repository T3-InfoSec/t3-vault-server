
from app.services.connection_manager import ConnectionManager
from sqlalchemy.orm import Session


async def handle_exit(client_id: str, connection_manager: ConnectionManager,db:Session):
    # Handle exit logic here
    await connection_manager.disconnect_client(client_id,db)
    print(f"Client {client_id} disconnected")
