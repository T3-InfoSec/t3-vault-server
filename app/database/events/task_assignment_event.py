print("Task events module loaded - registering listeners")

from sqlalchemy.orm import Session
from app.database.models.solver import Solver
from app.database.models.task import Task
from sqlalchemy import event
from sqlalchemy.engine import Connection
from typing import Any
import logging


from app.database.models.task_assignment import TaskAssignment
from app.services import connection_manager
from app.services.message_handlers.tlp_handler import (
    handle_tlp_task_assignment_assign_to_solver,
)
from app.utils.fingerprint import Fingerprint

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Method 1: Using the event decorator
@event.listens_for(TaskAssignment, "after_insert")
def on_task_assignment_insert(
    mapper: Any, connection: Connection, target: TaskAssignment
) -> None:
    """
    Listener that triggers after a Task instance is inserted.

    Args:
        mapper: The Mapper object which is the target of the event
        connection: The Connection object which is being used to emit SQL
        target: The instance being inserted (your Task object)
    """

    session = Session(bind=connection)

    #

    solver_id = target.solver_id
    print(f"New task assignment inserted with db_key: {target.db_key}")
    print(f"Solver ID: {solver_id}")
    print(f"Created at: {target.created_at}")
    # get conn manager
    solver = session.query(Solver).filter_by(db_key=solver_id).first()
    task = session.query(Task).filter_by(db_key=target.db_key).first()
    handle_tlp_task_assignment_assign_to_solver(
        assignment=target,
        solver=solver,
        task=task,
        db=session,
    )
    # Add your custom logic here
