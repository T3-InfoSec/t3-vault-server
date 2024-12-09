from datetime import datetime
from app.database.models.task import Task
from app.database.models.task_assignment import TaskAssignment
from app.services.connection_manager import ConnectionManager
from sqlalchemy.orm import Session

from app.utils.encryption import Encryption


async def handle_solver_tlp_reponse(
    solver_id: str, connection_manager: ConnectionManager, data: dict, db: Session
):
    # Handle handle_solver_tlp_reponse logic here

    print(f"SOLVER {solver_id} responded with TLP response: {data}")
    assignment_key = data.get("assignment_key")
    answer = data.get("answer")

    # get task assignment by id
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

    # Update task assignment fields
    task_assignment.delivery_at = delivered_at
    task_assignment.elapsed_time = total_seconds
    task_assignment.validity = True

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
            "assignment_key": Encryption().fingerprint_to_hex(task_assignment.task_id),
            "answer": answer,
        },
    }
    await connection_manager.send_to_client_hx(client_key_hx=client_id_hx, message=data)

    # we update task assignment
