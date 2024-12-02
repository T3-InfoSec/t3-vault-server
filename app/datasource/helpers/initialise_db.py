
import asyncio
from app.datasource.table_methods.client_table_manager import ClientTableManager
from app.datasource.table_methods.complaints_table import ComplaintTableManager
from app.datasource.table_methods.solver_table import SolverTableManager
from app.datasource.table_methods.task_assignment_table import TaskAssignmentTableManager
from app.datasource.table_methods.task_table_manager import TaskTableManager


class InitialiseDatabase:
    def __init__(self, db_manager):
        """
        Initialize the InitialiseDatabase with a database manager.
        :param db_manager: Instance of AsyncDatabaseManager for database operations.
        """
        self.db_manager = db_manager        
        self.tables = [
            TaskTableManager(db_manager),
            TaskAssignmentTableManager(db_manager),
            SolverTableManager(db_manager),
            ClientTableManager(db_manager),
            ComplaintTableManager(db_manager),
        ]

    async def initialize_database(self):
        """
        Create all tables in the database and start listening for unassigned tasks.
        """
        # Create all tables
        for table_manager in self.tables:
            await table_manager.create_table()
        print("All tables have been successfully created.")
        # temp (TEST)
        await SolverTableManager(self.db_manager).add_or_update_solver(fingerprint_input="12345678901234567890123456789012")

        # Start the listener for unassigned tasks
        task_schema = TaskTableManager(db_manager=self.db_manager)
        
        # Create a background task for listening without blocking
        asyncio.create_task(task_schema.listen_for_unassigned_tasks(interval=15))

