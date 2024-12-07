from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from .database.database import get_db, Base, engine
from .services.connection_manager import ConnectionManager
import json

Base.metadata.create_all(bind=engine)

app = FastAPI()
connection_manager = ConnectionManager()

@app.websocket("/ws/client/{client_id}")
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

@app.websocket("/ws/solver/{solver_id}")
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)