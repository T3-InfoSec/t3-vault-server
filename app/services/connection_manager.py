from fastapi import WebSocket
from typing import Dict
import json
from sqlalchemy.orm import Session
from app.utils.encryption import Encryption
from app.database.models.client import Client
from app.database.models.solver import Solver
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConnectionManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ConnectionManager, cls).__new__(cls, *args, **kwargs)
            cls._instance._clients = {}
            cls._instance._solvers = {}
            cls._instance.encryption = Encryption()
        return cls._instance

    def __init__(self):
        pass  # Initialization logic is handled in __new__

    async def connect_client(
        self, websocket: WebSocket, client_key: str, db: Session
    ) -> None:
        """
        Connect a client to the manager and update its status in the database.
        """
        await websocket.accept()

        # Generate fingerprint from client key
        client_id = self.encryption.hex_to_fingerprint(client_key)
        hex_id = self.encryption.fingerprint_to_hex(client_id)
        print(f"Client ID: {client_key} and hex ID: {hex_id}")
        # Register the client in the connection manager
        self._clients[hex_id] = websocket
        logger.info(f"Client connected with hex ID: {hex_id}")

        # Update client connection status in database
        client = db.query(Client).filter(Client.client_id == client_id).first()
        if not client:
            client = Client(
                client_id=client_id, is_connected=True, connection_id=str(id(websocket))
            )
            db.add(client)
        else:
            client.is_connected = True
            client.connection_id = str(id(websocket))
        db.commit()

    async def connect_solver(
        self, websocket: WebSocket, solver_key: str, db: Session
    ) -> None:
        """
        Connect a solver to the manager and update its status in the database.
        """
        await websocket.accept()

        # Generate fingerprint from solver key
        solver_id = self.encryption.hex_to_fingerprint(solver_key)
        hex_id = self.encryption.fingerprint_to_hex(solver_id)
        print(f"Client ID: {solver_key} and hex ID: {hex_id}")

        # Register the solver in the connection manager
        self._solvers[hex_id] = websocket
        logger.info(f"Solver connected with hex ID: {hex_id}")

        # Update solver connection status in database
        solver = db.query(Solver).filter(Solver.solver_id == solver_id).first()
        if not solver:
            solver = Solver(
                solver_id=solver_id, is_online=True, connection_id=str(id(websocket))
            )
            db.add(solver)
        else:
            solver.is_online = True
            solver.connection_id = str(id(websocket))
        db.commit()

    async def disconnect_client(self, client_key: str, db: Session) -> None:
        """
        Disconnect a client and update its status in the database.
        """
        client_id = self.encryption.hex_to_fingerprint(client_key)
        hex_id = self.encryption.fingerprint_to_hex(client_id)

        if hex_id in self._clients:
            del self._clients[hex_id]
            logger.info(f"Client disconnected with hex ID: {hex_id}")

            client = db.query(Client).filter(Client.client_id == client_id).first()
            if client:
                client.is_connected = False
                client.connection_id = None
                db.commit()

    async def disconnect_solver(self, solver_key: str, db: Session) -> None:
        """
        Disconnect a solver and update its status in the database.
        """
        solver_id = self.encryption.hex_to_fingerprint(solver_key)
        hex_id = self.encryption.fingerprint_to_hex(solver_id)

        if hex_id in self._solvers:
            del self._solvers[hex_id]
            logger.info(f"Solver disconnected with hex ID: {hex_id}")

            solver = db.query(Solver).filter(Solver.solver_id == solver_id).first()
            if solver:
                solver.is_online = False
                solver.connection_id = None
                db.commit()

    async def send_to_client(self, client_key: str, message: dict) -> None:
        """
        Send a message to a connected client using its key.
        """
        client_id = self.encryption.hex_to_fingerprint(client_key)
        hex_id = self.encryption.fingerprint_to_hex(client_id)

        if hex_id in self._clients:
            encrypted_message = self.encryption.encrypt(json.dumps(message),passsword=client_key)
            await self._clients[hex_id].send_bytes(encrypted_message)

    async def send_to_client_hx(self, client_key_hx: str, message: dict) -> None:
        """
        Send a message to a connected client using its hex ID.
        """
        if client_key_hx in self._clients:
            encrypted_message = self.encryption.encrypt(json.dumps(message),passsword=client_key_hx)
            await self._clients[client_key_hx].send_bytes(encrypted_message)

    async def send_to_solver(self, solver_key: str, message: dict) -> None:
        """
        Send a message to a connected solver using its key.
        """
        solver_id = self.encryption.hex_to_fingerprint(solver_key)
        hex_id = self.encryption.fingerprint_to_hex(solver_id)
        logger.info(f"Sending message to solver with hex ID: {hex_id}")

        if hex_id in self._solvers:
            encrypted_message = self.encryption.encrypt(json.dumps(message),passsword=solver_key)
            await self._solvers[hex_id].send_bytes(encrypted_message)

    async def send_to_solver_hx(self, fingerprint: bytes, message: dict) -> None:
        """
        Send a message to a connected solver using its fingerprint (bytes).
        """
        hex_id = self.encryption.fingerprint_to_hex(fingerprint)
        logger.info(f"Sending message to solver with hex ID hx: {hex_id}")
        print(f"FOUND SOLVER {self._solvers}")
        if hex_id in self._solvers:
            print("WELL FOUND SOLVER")
            encrypted_message = self.encryption.encrypt(json.dumps(message),passsword=hex_id)
            await self._solvers[hex_id].send_bytes(encrypted_message)


connection_manager = ConnectionManager()
