# app/services/connection_manager.py
from fastapi import WebSocket
from typing import Dict, Optional
import json
from ..utils.encryption import Encryption
from ..database.models import Client, Solver
from sqlalchemy.orm import Session

class ConnectionManager:
    def __init__(self):
        self._clients: Dict[str, WebSocket] = {}
        self._solvers: Dict[str, WebSocket] = {}
        self.encryption = Encryption()
    
    async def connect_client(self, websocket: WebSocket, client_id: str, db: Session) -> None:
        await websocket.accept()
        self._clients[client_id] = websocket
        
        # Update client connection status in database
        client = db.query(Client).filter(Client.client_id == client_id).first()
        if not client:
            client = Client(
                client_id=client_id,
                is_connected=True,
                connection_id=str(id(websocket))
            )
            db.add(client)
        else:
            client.is_connected = True
            client.connection_id = str(id(websocket))
        db.commit()
    
    async def connect_solver(self, websocket: WebSocket, solver_id: str, db: Session) -> None:
        await websocket.accept()
        self._solvers[solver_id] = websocket
        
        # Update solver connection status in database
        solver = db.query(Solver).filter(Solver.solver_id == solver_id).first()
        if not solver:
            solver = Solver(
                solver_id=solver_id,
                is_online=True,
                connection_id=str(id(websocket))
            )
            db.add(solver)
        else:
            solver.is_online = True
            solver.connection_id = str(id(websocket))
        db.commit()
    
    async def disconnect_client(self, client_id: str, db: Session) -> None:
        if client_id in self._clients:
            del self._clients[client_id]
            client = db.query(Client).filter(Client.client_id == client_id).first()
            if client:
                client.is_connected = False
                client.connection_id = None
                db.commit()
    
    async def disconnect_solver(self, solver_id: str, db: Session) -> None:
        if solver_id in self._solvers:
            del self._solvers[solver_id]
            solver = db.query(Solver).filter(Solver.solver_id == solver_id).first()
            if solver:
                solver.is_online = False
                solver.connection_id = None
                db.commit()

    async def send_to_client(self, client_id: str, message: dict) -> None:
        if client_id in self._clients:
            encrypted_message = self.encryption.encrypt(json.dumps(message))
            await self._clients[client_id].send_bytes(encrypted_message)
    
    async def send_to_solver(self, solver_id: str, message: dict) -> None:
        if solver_id in self._solvers:
            encrypted_message = self.encryption.encrypt(json.dumps(message))
            await self._solvers[solver_id].send_bytes(encrypted_message)
