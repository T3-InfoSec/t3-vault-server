# app/routes/client_ws.py
from fastapi import WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
import json

from app.database.database import get_db
from app.services.connection_manager import ConnectionManager

connection_manager = ConnectionManager()

async def client_websocket(
    websocket: WebSocket,
    client_id: str,
    db: Session = Depends(get_db)
):
    try:
        await connection_manager.connect_client(websocket, client_id, db)
        
        while True:
            # Receive and decrypt message
            encrypted_data = await websocket.receive_bytes()
            message = json.loads(connection_manager.encryption.decrypt(encrypted_data))
            
            # Process message based on type
            if message.get("type") == "ping":
                await connection_manager.send_to_client(client_id, {"type": "pong"})
            # Add more message type handlers here
            
    except WebSocketDisconnect:
        await connection_manager.disconnect_client(client_id, db)
