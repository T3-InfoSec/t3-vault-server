from fastapi import WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
import json
import time

from app.database.database import get_db
from app.database.models.solver import Solver
from app.services.connection_manager import connection_manager
from app.models.message_type import MessageSolverResponseType
from app.services.message_handlers.handler import MESSAGE_SOLVER_RESPONSE_TYPE_HANDLERS
from app.utils.encryption import Encryption


RATE_LIMIT_WINDOW = 10
MAX_REQUESTS_PER_WINDOW = 20
BAN_DURATION = 300

# Track solver request frequencies
solver_request_tracker = {}
banned_solvers = {}


async def solver_websocket(
    websocket: WebSocket, solver_id: str, db: Session = Depends(get_db)
):
    try:
        # Connect solver
        await connection_manager.connect_solver(websocket, solver_id, db)
        enc = Encryption()

        while True:
            # Check if the solver is banned
            current_time = time.time()
            if solver_id in banned_solvers:
                ban_expiration = banned_solvers[solver_id]
                if current_time < ban_expiration:
                    await websocket.close()
                    return
                else:
                    del banned_solvers[solver_id]

            # Receive and decrypt message
            encrypted_data = await websocket.receive_text()
            message = json.loads(enc.decrypt(encrypted_data, password=solver_id))

            # Track request frequency
            if solver_id not in solver_request_tracker:
                solver_request_tracker[solver_id] = []
            solver_request_tracker[solver_id].append(current_time)

            # Remove timestamps outside the time window
            solver_request_tracker[solver_id] = [
                t
                for t in solver_request_tracker[solver_id]
                if current_time - t <= RATE_LIMIT_WINDOW
            ]

            # Check if the request rate exceeds the limit
            if len(solver_request_tracker[solver_id]) > MAX_REQUESTS_PER_WINDOW:
                # Disconnect and ban the solver
                banned_solvers[solver_id] = current_time + BAN_DURATION
                await websocket.close()
                await reduce_solver_reputation(solver_id, db)
                print(f"Solver {solver_id} banned for exceeding request rate.")
                return

            # Handle the message
            message_type = message.get("type")
            data = message.get("data", {})
            try:
                message_enum = MessageSolverResponseType(message_type)
                handler = MESSAGE_SOLVER_RESPONSE_TYPE_HANDLERS.get(message_enum)
                if handler:
                    if message_enum in [
                        MessageSolverResponseType.TLP_RESPONSE,
                        MessageSolverResponseType.STATUS_UPDATE,
                        MessageSolverResponseType.PING,
                    ]:
                        await handler(solver_id, connection_manager, data, db)
                    else:
                        print(f"Unhandled message type: {message_type}")
                else:
                    print(f"Unhandled message type: {message_type}")
            except ValueError:
                print(f"Invalid message type: {message_type}")

    except WebSocketDisconnect:
        await connection_manager.disconnect_solver(solver_id, db)


async def reduce_solver_reputation(solver_id: str, db: Session):
    """Reduce the reputation of the solver in the database."""
    solver = db.query(Solver).filter(Solver.id == solver_id).first()
    if solver:
        solver.reputation_score = max(0, solver.reputation - 10)
        db.commit()
        print(f"Solver {solver_id} reputation reduced to {solver.reputation}.")
