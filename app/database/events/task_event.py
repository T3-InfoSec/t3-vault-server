print("Task events module loaded - registering listeners")

from sqlalchemy.orm import Session
from app.database.models.task import Task
from sqlalchemy import event
from sqlalchemy.engine import Connection
from typing import Any
import logging

from app.services.message_handlers.tlp_handler import handle_tlp_task_assignment_creation
from app.utils.fingerprint import Fingerprint

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Method 1: Using the event decorator
@event.listens_for(Task, 'after_insert')
def on_task_insert(mapper: Any, connection: Connection, target: Task) -> None:
    """
    Listener that triggers after a Task instance is inserted.
    
    Args:
        mapper: The Mapper object which is the target of the event
        connection: The Connection object which is being used to emit SQL
        target: The instance being inserted (your Task object)
    """
    
    session = Session(bind=connection)

    # 
    hext= Fingerprint.fingerprint_to_hex(target.client_id)
    print(f"New task inserted with db_key: {target.db_key}")
    print(f"Client ID: {hext}")
    print(f"Created at: {target.created_at}")
    handle_tlp_task_assignment_creation(task=target,db=session)
    # Add your custom logic here
