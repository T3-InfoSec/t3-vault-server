from datetime import datetime
import json
from app.database.database import get_db
from app.models.message_type import MessageResponseType, MessageType
from app.services.connection_manager import ConnectionManager
from sqlalchemy.orm import Session
from app.database.models.task import Task
from app.utils.encryption import Encryption
from fastapi import WebSocket, WebSocketDisconnect, Depends


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
            fingerprint=fingerprint,
            difficulty=1,
        ),
    )
    db.commit()


def handle_tlp_task_assignment(task: Task):

    db_generator = get_db()
    db = next(db_generator)
    # get a solver

    print("Handling TLP task assignment")
    # response_data = {"answer": "123", "fingerprint": "1234f"}
    # await connection_manager.send_to_client(
    #     client_id,
    #     {
    #         "type": f"{MessageResponseType.TLP_RESPONSE.value}",
    #         "data": json.dumps(response_data),
    #     },
    # )
