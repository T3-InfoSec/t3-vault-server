from fastapi import WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
import json

from app.database.database import get_db
from app.database.models.solver import Solver
from app.services.connection_manager import ConnectionManager

connection_manager = ConnectionManager()

async def solver_websocket(
    websocket: WebSocket,
    solver_id: str,
    db: Session = Depends(get_db)
):
    try:
        await connection_manager.connect_solver(websocket, solver_id, db)
        
        while True:
            # Receive and decrypt message
            encrypted_data = await websocket.receive_bytes()
            message = json.loads(connection_manager.encryption.decrypt(encrypted_data))
            
            # Process message based on type
            if message.get("type") == "status_update":
                solver = db.query(Solver).filter(Solver.solver_id == solver_id).first()
                if solver:
                    solver.is_online = message.get("is_online", True)
                    db.commit()
            # Add more message type handlers here
            
    except WebSocketDisconnect:
        await connection_manager.disconnect_solver(solver_id, db)
