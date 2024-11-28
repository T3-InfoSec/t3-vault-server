from app.datasource.helpers.hash_helper import generate_secure_hash


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
        difficulty INTEGER,
        parameter_t BIGINT,
        input_fingerprint INTEGER,
        assignments_count INTEGER DEFAULT 0
        """
        await self.db_manager.create_table("tasks", schema)

    async def add_task(self, difficulty, parameter_t, created_at=None, client_id=0):
        """
        Add a new task to the database.
        :param difficulty: The difficulty level of the task (integer).
        :param parameter_t: A large parameter value for the task (big integer).
        :param created_at: Timestamp of creation (default: current time).
        :param client_id: The client's unique ID (integer, optional).
        """
        if not created_at:
            created_at = "DATETIME('now')"

        # Prepare input string for hash generation
        input_string = f"{client_id or 0}:{created_at}:{parameter_t}"

        input_fingerprint = generate_secure_hash(input_string)

        await self.db_manager.insert(
            "tasks",
            (
                None,
                created_at,
                client_id,
                difficulty,
                parameter_t,
                input_fingerprint,
                0,
            ),
        )

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
