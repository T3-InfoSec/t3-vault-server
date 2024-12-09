from fastapi import WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
import json

from app.database.database import get_db
from app.database.models.solver import Solver
from app.services.connection_manager import connection_manager
from app.models.message_type import MessageSolverResponseType, MessageType
from app.services.message_handlers.handler import MESSAGE_SOLVER_RESPONSE_TYPE_HANDLERS, MESSAGE_TYPE_HANDLERS
from app.utils.encryption import Encryption



async def solver_websocket(
    websocket: WebSocket, solver_id: str, db: Session = Depends(get_db)
):
    try:
        await connection_manager.connect_solver(websocket, solver_id, db)
        enc = Encryption()
        
        while True:
            # Receive and decrypt message
            encrypted_data = await websocket.receive_text()
            message = json.loads(enc.decrypt(encrypted_data))
            # Get message type and data
            message_type = message.get("type")
            data = message.get("data", {})
            # handle message by type
            # Dispatch message handling
            try:
                message_enum = MessageSolverResponseType(message_type)
                handler = MESSAGE_SOLVER_RESPONSE_TYPE_HANDLERS.get(message_enum)
                if handler:
                    # Pass additional arguments if required
                    if message_enum in [MessageSolverResponseType.TLP_RESPONSE,MessageSolverResponseType.STATUS_UPDATE,MessageSolverResponseType.PING]:
                        await handler(solver_id, connection_manager, data,db)
                    else:
                       print(f"Unhandled message type: {message_type}")
                else:
                    print(f"Unhandled message type: {message_type}")
            except ValueError:
                print(f"Invalid message type: {message_type}")            
    except WebSocketDisconnect:
        await connection_manager.disconnect_solver(solver_id, db)
