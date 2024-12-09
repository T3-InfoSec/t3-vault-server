from app.services.connection_manager import ConnectionManager
from sqlalchemy.orm import Session


async def handle_solver_tlp_reponse(
    solver_id: str, connection_manager: ConnectionManager, data: dict, db: Session
):
    # Handle handle_solver_tlp_reponse logic here

    print(f"SOLVER {solver_id} responded")
