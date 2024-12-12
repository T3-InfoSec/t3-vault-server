from fastapi import WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
import json

from app.database.database import get_db
from app.models.message_type import MessageType

from app.services.connection_manager import connection_manager
from app.services.message_handlers.handler import MESSAGE_TYPE_HANDLERS
from app.utils.boostrap_db_datas import bootstrap_data
from app.utils.encryption import Encryption





async def client_websocket(
    websocket: WebSocket,
    client_id: str,
    db: Session = Depends(get_db)
):
    try:        
        await connection_manager.connect_client(websocket, client_id, db)

        while True:
            # Receive and decrypt message
            enc = Encryption()
            encrypted_data = await websocket.receive_text()
            message = json.loads(enc.decrypt(encrypted_data))
            print(f"Received message: {message}")

            # Get message type and data
            message_type = message.get("type")
            data = message.get("data", {})

            # Dispatch message handling
            try:
                message_enum = MessageType(message_type)
                handler = MESSAGE_TYPE_HANDLERS.get(message_enum)
                if handler:
                    # Pass additional arguments if required
                    if message_enum in [MessageType.TLP, MessageType.COMPLAINT]:
                        await handler(client_id, connection_manager, data,db)
                    else:
                        await handler(client_id, connection_manager,db)
                else:
                    print(f"Unhandled message type: {message_type}")
            except ValueError:
                print(f"Invalid message type: {message_type}")

    except WebSocketDisconnect:
        await connection_manager.disconnect_client(client_id, db)
