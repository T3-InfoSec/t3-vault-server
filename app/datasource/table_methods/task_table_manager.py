import asyncio
from datetime import datetime, timedelta
from app.datasource.helpers.hash_helper import generate_secure_hash
from app.datasource.table_methods.task_assignment_table import TaskAssignmentTableManager


class TaskTableManager:
    def __init__(self, db_manager):
        """
        Initialize the TaskTableManager with a database manager.
        :param db_manager: Instance of AsyncDatabaseManager for database operations.
        """
        self.db_manager = db_manager

    async def create_table(self):
        """
        Create the 'tasks' table with the specified schema if it doesn't exist.
        """
        schema = """
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT DEFAULT (DATETIME('now')),
        client_id INTEGER DEFAULT 0,
        difficulty INTEGER NOT NULL,
        parameter_t BIGINT NOT NULL,
        input_fingerprint INTEGER NOT NULL,
        first_assignment_id INTEGER DEFAULT NULL,
        second_assignment_id INTEGER DEFAULT NULL,
        assignments_count INTEGER DEFAULT 0,
        payment_info_id INTEGER DEFAULT NULL
        """
        await self.db_manager.create_table("tasks", schema)

    async def add_task(
        self, difficulty, parameter_baseg, parameter_product, parameter_t, client_id=0
    ):
        """
        Add a new task to the database.
        :param difficulty: The difficulty level of the task (integer).
        :param parameter_t: A large parameter value for the task (big integer).
        :param created_at: Timestamp of creation (default: current time).
        :param client_id: The client's unique ID (integer, optional).
        """

        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Generate a cryptographic fingerprint for the task's input
        input_string = f"{client_id}:{created_at}:{parameter_baseg}:{parameter_product}"
        input_fingerprint = generate_secure_hash(input_string)

        await self.db_manager.insert(
            "tasks",
            (
                None,  # id (autoincrement)
                created_at,
                client_id,  # client_id
                difficulty,  # difficulty
                parameter_t,  # parameter_t
                input_fingerprint,  # input_fingerprint
                None,  # first_assignment_id
                None,  # second_assignment_id
                0,  # assignments_count
                None,  # payment_info_id
            ),
        )
        return input_fingerprint

    async def update_task(self, task_id, updates):
        """
        Update a task's information.
        :param task_id: The task's unique ID (integer).
        :param updates: Dictionary containing the updates (keys are column names).
        """
        set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
        params = list(updates.values()) + [task_id]
        await self.db_manager.update("tasks", set_clause, "id = ?", params)

    async def get_task(self, task_id):
        """
        Retrieve a task's data by its ID.
        :param task_id: The task's unique ID (integer).
        :return: Dictionary representing the task's data, or None if not found.
        """
        rows = await self.db_manager.read(
            "SELECT * FROM tasks WHERE id = ?", (task_id,)
        )
        return dict(rows[0]) if rows else None
    async def get_task_by_fingerprint(self,fingerprint):
        """
        Retrieve a task's data by its fingerprint.
        :param fingerprint: The task's fingerprint (string).
        :return: Dictionary representing the task's data, or None if not found.
        """
        rows = await self.db_manager.read(
            "SELECT * FROM tasks WHERE input_fingerprint = ?", (fingerprint,)
        )
        return dict(rows[0]) if rows else None
    async def get_tasks_by_client(self, client_id):
        """
        Retrieve all tasks assigned to a specific client.
        :param client_id: The client's unique ID (integer).
        :return: List of dictionaries representing the tasks.
        """
        rows = await self.db_manager.read(
            "SELECT * FROM tasks WHERE client_id = ?", (client_id,)
        )
        return [dict(row) for row in rows]

    async def get_tasks_by_difficulty(self, difficulty):
        """
        Retrieve all tasks with a specific difficulty level.
        :param difficulty: The difficulty level (integer).
        :return: List of dictionaries representing the tasks.
        """
        rows = await self.db_manager.read(
            "SELECT * FROM tasks WHERE difficulty = ?", (difficulty,)
        )
        return [dict(row) for row in rows]

    async def delete_task(self, task_id):
        """
        Delete a task by its ID.
        :param task_id: The task's unique ID (integer).
        """
        await self.db_manager.delete("tasks", "id = ?", (task_id,))

    from datetime import datetime, timedelta

    async def listen_for_unassigned_tasks(self, interval=1):
        """
        Continuously listen for new unassigned tasks being added to the database.
        :param interval: Time interval in seconds for polling.
        """
        last_task_id = 0  # Variable to keep track of the last seen task ID

        while True:
            # Query for new unassigned tasks where assignments_count is 0
            rows = await self.db_manager.read(
                "SELECT * FROM tasks WHERE assignments_count = 0 AND id > ? ORDER BY created_at ASC",
                (last_task_id,),
            )
            new_tasks = [dict(row) for row in rows]

            # If there are new unassigned tasks, process them
            for task in new_tasks:
                print(f"New unassigned task detected: {task}")
                last_task_id = task["id"]
                task_key = task["input_fingerprint"]

                # Create a task assignment
                assignment = await TaskAssignmentTableManager(db_manager=self.db_manager).add_task_assignment(
                    task_id=last_task_id,
                    task_key=task_key,
                    solver_id=1,
                    delivery_deadline=(datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S"),
                    complaint_deadline=(datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),
                )

                if assignment:
                    # Directly update the task in the database
                    await self.db_manager.custom_query(
                        """
                        UPDATE tasks
                        SET first_assignment_id = ?, assignments_count = assignments_count + 1
                        WHERE id = ?
                        """,
                        (assignment["id"], last_task_id),
                    )
                    print(f"Task {last_task_id} updated with assignment ID {assignment['id']}.")

            # Wait before the next check
            await asyncio.sleep(interval)
