from datetime import datetime, timedelta
import json
import math
from app.database.database import get_db
from app.database.models.client import Client
from app.database.models.solver import Solver
from app.database.models.task_assignment import TaskAssignment
from app.services.connection_manager import ConnectionManager, connection_manager
from sqlalchemy.orm import Session
from app.database.models.task import Task
from app.utils.encryption import Encryption
import asyncio


async def handle_tlp_task_creation(
    client_id: str, connection_manager: ConnectionManager, data: dict, db: Session
):
    enc = Encryption()
    current_datetime = datetime.now()
    parameter_t = data.get("t")
    parameter_baseg = data.get("baseg")
    parameter_product = data.get("product") 
    dificulty = (math.floor(math.log2(int(parameter_product))) + 1) / (int(parameter_t) or 1)

    print(f"parameter_t: {parameter_t} parameter_baseg: {parameter_baseg} parameter_product: {parameter_product}")
    fingerprint_string = f"{parameter_baseg}{parameter_product}{current_datetime}"
    client_id_f = enc.generate_fingerprint(client_id)
    fingerprint = enc.generate_fingerprint(fingerprint_string)
    # dificulty should be calculated based on the difficulty of the task (e.g. number of bits)
    db.add(
        Task(
            client_id=client_id_f,
            parameter_t=parameter_t,
            parameter_product=enc.encrypt(parameter_product),
            parameter_baseg=enc.encrypt(parameter_baseg),
            fingerprint=fingerprint,
            difficulty=dificulty,
        ),
    )
    # get cleint from client id
    client = db.query(Client).filter(Client.client_id == client_id_f).first()
    client.tasks_requested = client.tasks_requested + 1
    db.commit()


def handle_tlp_task_assignment_creation(task: Task, db: Session):
    # querry a solver that is is_online=1; later make sure to get the best reputation    
    solver = db.query(Solver).filter_by(is_online=1).first()
    if not solver:
        print("No solver found")
        # when a solver comes online later we can revisit this
        return
    solver.tasks_taken  = solver.tasks_taken + 1
    # 
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

    # get task
    task = db.query(Task).filter(Task.fingerprint == task.fingerprint).first()
    if(task.first_assignment_id  is None):
        task.first_assignment_id = task_assignment.db_key
    else:        
        if(task.second_assignment_id is None):
            task.second_assignment_id = task_assignment.db_key
    task.num_assignments = task.num_assignments + 1
    db.commit()
def handle_tlp_task_assignment_assign_to_solver(
    assignment: TaskAssignment,
    solver: Solver,
    task: Task,
    db: Session,
):
    print(f"Handling TLP task assignment for task {task.db_key}")
    solver_fingerprint = solver.solver_id
    enc = Encryption()
    t = task.parameter_t
    product = enc.decrypt(task.parameter_product)
    baseg = enc.decrypt(task.parameter_baseg)
    assignment_key = assignment.db_key
    message = {
        "type": "tlpSolverRequest",
        "data": {
            "t": t,
            "baseg": baseg,
            "product": product,
            "assignment_key": assignment_key,
        },
    }
    
    loop = asyncio.get_event_loop()
    loop.create_task(
        connection_manager.send_to_solver_hx(
            fingerprint=solver_fingerprint, message=message
        )
    )
    print("Task assignment handling scheduled")
