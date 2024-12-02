from datetime import datetime


class TaskAssignmentTableManager:
    def __init__(self, db_manager):
        """
        Initialize the TaskAssignmentTableManager with a database manager.
        :param db_manager: Instance of AsyncDatabaseManager for database operations.
        """
        self.db_manager = db_manager

    async def create_table(self):
        """
        Create the 'task_assignments' table with the specified schema if it doesn't exist.
        The 'created_at' column is automatically set to the current date and time.
        """
        schema = """
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id INTEGER NOT NULL,
        created_at TEXT DEFAULT (DATETIME('now')),
        delivery_time TEXT,
        delivery_deadline TEXT,
        complaint_deadline TEXT,
        elapsed_time INTEGER DEFAULT 0,
        delivered_in_time TEXT DEFAULT NULL, -- 'delivered' or 'expired'
        complaint_id INTEGER DEFAULT NULL,
        response_power INTEGER DEFAULT 0,
        complaint_time TEXT DEFAULT NULL,
        validity TEXT DEFAULT NULL, -- 'good' or 'bad'
        solver_id INTEGER,
        task_key binary(16) NOT NULL,
        FOREIGN KEY (task_id) REFERENCES tasks (id),
        FOREIGN KEY (solver_id) REFERENCES solvers (id)
        """
        await self.db_manager.create_table("task_assignments", schema)


    async def add_task_assignment(
        self,
        task_id,
        delivery_deadline,
        complaint_deadline,
        solver_id,
        task_key,
        delivery_time=None,
        complaint_id=None,
        response_power=0,
        complaint_time=None,
        delivered_in_time=None,
        validity=None,
    ):
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        """
        Add a new task assignment to the database and return the created assignment.
        """
        # Insert the new task assignment
        await self.db_manager.insert(
            "task_assignments",
            (
                None,  # id (autoincrement)
                task_id,
                created_at,
                delivery_time,
                delivery_deadline,
                complaint_deadline,
                0,  # elapsed_time starts at 0
                delivered_in_time,
                complaint_id,
                response_power,
                complaint_time,
                validity,
                solver_id,
                task_key,
            ),
        )

        # Retrieve the last inserted task assignment
        row = await self.db_manager.read(
            "SELECT * FROM task_assignments WHERE ROWID = last_insert_rowid()"
        )

        # Return the newly created task assignment as a dictionary
        return dict(row[0]) if row else None

    async def update_task_assignment(self, assignment_id, updates):
        """
        Update a task assignment's information.
        """
        set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
        params = list(updates.values()) + [assignment_id]
        await self.db_manager.update("task_assignments", set_clause, "id = ?", params)

    async def get_task_assignment(self, assignment_id):
        """
        Retrieve a task assignment's data by its ID.
        """
        rows = await self.db_manager.read(
            "SELECT * FROM task_assignments WHERE id = ?",
            (assignment_id,),
        )
        return dict(rows[0]) if rows else None

    async def get_assignments_by_task(self, task_key):
        """
        Retrieve all assignments for a specific task.
        """
        rows = await self.db_manager.read(
            "SELECT * FROM task_assignments WHERE task_key = ?",
            (task_key,),
        )
        return [dict(row) for row in rows]

    async def get_assignments_by_solver(self, solver_id):
        """
        Retrieve all task assignments for a specific solver by their solver_id.
        :param solver_id: The solver's unique ID (integer).
        :return: List of dictionaries representing the task assignments.
        """
        rows = await self.db_manager.read(
            "SELECT * FROM task_assignments WHERE solver_id = ?",
            (solver_id,),
        )
        return [dict(row) for row in rows]

    async def delete_task_assignment(self, assignment_id):
        """
        Delete a task assignment by its ID.
        """
        await self.db_manager.delete("task_assignments", "id = ?", (assignment_id,))
