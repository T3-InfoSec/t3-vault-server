from datetime import datetime, timedelta
import json
from app.database.database import get_db
from app.database.models.solver import Solver
from app.database.models.task_assignment import TaskAssignment
from app.models.message_type import MessageResponseType, MessageType
from app.services.connection_manager import ConnectionManager
from sqlalchemy.orm import Session
from app.database.models.task import Task
from app.utils.encryption import Encryption
from fastapi import WebSocket, WebSocketDisconnect, Depends
import asyncio


async def handle_tlp_task_creation(
    client_id: str, connection_manager: ConnectionManager, data: dict, db: Session
):
    parameter_t = int(data.get("t"))
    parameter_baseg = int(data.get("baseg"))
    parameter_product = int(data.get("product"))
    current_datetime = datetime.now()
    fingerprint_string = f"{parameter_baseg}{parameter_product}{current_datetime}"
    client_id_f = Encryption.generate_fingerprint(client_id)
    fingerprint = Encryption.generate_fingerprint(fingerprint_string)
    db.add(
        Task(
            client_id=client_id_f,
            parameter_t=parameter_t,
            parameter_product=parameter_product,
            parameter_baseg=parameter_baseg,
            fingerprint=fingerprint,
            difficulty=1,
        ),
    )
    db.commit()


def handle_tlp_task_assignment_creation(task: Task, db: Session):
    # querry a solver that is is_online=1; later make sure to get the best reputation
    solver = db.query(Solver).filter_by(is_online=1).first()
    if not solver:
        print("No solver found")
        # when a solver comes online later we can revisit this
        return
    deadline = datetime.now() + timedelta(hours=8)
    complaint_deadline = datetime.now() + timedelta(hours=24)
    task_assignment = TaskAssignment(
        task_id=task.fingerprint,
        solver_id=solver.db_key,
        task_key=task.db_key,
        deadline=deadline,
        complaint_deadline=complaint_deadline,
    )
    db.add(task_assignment)
    db.commit()


def handle_tlp_task_assignment_assign_to_solver(
    assignment: TaskAssignment, solver: Solver, task: Task, db: Session
):
    print(f"Handling TLP task assignment for task {task.db_key}")

    solver_fingerprint = solver.solver_id
    
    t = task.parameter_t
    product = task.parameter_product
    baseg = task.parameter_baseg
    assignment_key = assignment.db_key
    message = {
        "type": "tlpSolverRequest",
        "data": "{'t':%s,'baseg':%s,'product':%s,assignment_key:%s}" % (t, baseg, product,assignment_key),
    }
    # make only this async so i can await
    loop = asyncio.get_event_loop()
    loop.create_task(ConnectionManager().send_to_solver_hx(fingerprint=solver_fingerprint, message=message))
    print("Task assignment handling scheduled")

    print("Handling TLP task assignment")


# response_data = {"answer": "123", "fingerprint": "1234f"}
# await connection_manager.send_to_client(
#     client_id,
#     {
#         "type": f"{MessageResponseType.TLP_RESPONSE.value}",
#         "data": json.dumps(response_data),
#     },
# )
