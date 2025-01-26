from datetime import datetime
from app.database.models.client import Client
from app.database.models.provider import Provider
from app.database.models.task import Task
from app.database.models.task_assignment import TaskAssignment
from app.services.connection_manager import ConnectionManager
from sqlalchemy.orm import Session

from app.utils.encryption import Encryption


async def handle_solver_tlp_reponse(
    solver_key: str, connection_manager: ConnectionManager, data: dict, db: Session
):
    # Handle handle_solver_tlp_reponse logic here
    enc = Encryption()
    solver_id = enc.generate_fingerprint(solver_key)
    print(f"SOLVER {enc.fingerprint_to_hex(solver_id)} responded with TLP response: {data}")
    assignment_key = data.get("assignment_key")
    answer = data.get("answer")
    
    task_assignment = (
        db.query(TaskAssignment)
        .filter(TaskAssignment.db_key == assignment_key)
        .first()
    )

    # Calculate the delivery time and elapsed time
    created_at = task_assignment.created_at
    delivered_at = datetime.now()
    time_elapsed = delivered_at - created_at
    total_seconds = time_elapsed.total_seconds()
    deadline = task_assignment.deadline
    # a boolean checks if 
    delivered_in_time = delivered_at < deadline    
    # Update task assignment fields
    task_assignment.delivery_at = delivered_at
    task_assignment.elapsed_time = total_seconds
    task_assignment.validity = True
    task_assignment.delivered_in_time = delivered_in_time
    # update solver's rep
    # get solver 
    solver = db.query(Provider).filter(Provider.solver_id == solver_id).first()
    if not delivered_in_time:
        solver.tasks_expired = solver.tasks_expired + 1
    solver.tasks_delivered  = solver.tasks_delivered + 1
    # make better reputation score
    solver.reputation_score = 0.05 * solver.success_rate + 1
    # Commit the changes to the database
    db.commit()
    # get client from assignment
    task_id = task_assignment.task_id
    # get task from task id
    task = db.query(Task).filter(Task.fingerprint == task_id).first()
    # get client from task
    client_id_hx = Encryption().fingerprint_to_hex(task.client_id)
    data = {
        "type": "tlpResponse",
        "data": {
            "fingerprint": Encryption().fingerprint_to_hex(task_assignment.task_id),
            "answer": str(answer),
        },
    }
    await connection_manager.send_to_client_hx(client_key_hx=client_id_hx, message=data)
    client = db.query(Client).filter(Client.client_id == task.client_id).first()
    client.tasks_received = client.tasks_received + 1
    db.commit()
    # we update task assignment
