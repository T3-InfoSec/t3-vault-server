from app.datasource.helpers.hash_helper import generate_secure_hash


class ComplaintTableManager:
    def __init__(self, db_manager):
        """
        Initialize the ComplaintTableManager with a database manager.
        :param db_manager: Instance of AsyncDatabaseManager for database operations.
        """
        self.db_manager = db_manager

    async def create_table(self):
        """
        Create the 'complaints' table with the specified schema if it doesn't exist.
        """
        schema = """
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT DEFAULT (DATETIME('now')),
        client_id INTEGER DEFAULT NULL,
        solver_id INTEGER NOT NULL,
        arbiter_id INTEGER DEFAULT 3099,
        task_assignment_id INTEGER NOT NULL,
        solved_at TEXT DEFAULT NULL,
        result INTEGER DEFAULT NULL,
        fingerprint INTEGER NOT NULL
        """
        await self.db_manager.create_table('complaints', schema)

    async def add_complaint(self, client_id, solver_id, task_assignment_id, solved_at=None, result=None):
        """
        Add a new complaint to the database.
        :param client_id: The client's ID (integer or None).
        :param solver_id: The solver's ID (integer).
        :param task_assignment_id: The ID of the task assignment (integer).
        :param solved_at: The resolution timestamp (string or None).
        :param result: The resolution result (0 or 1, or None if undecided).
        """
        created_at = "DATETIME('now')"
        fingerprint = generate_complaint_fingerprint(client_id, solver_id, created_at, solved_at, result)

        await self.db_manager.insert(
            'complaints',
            (None, created_at, client_id, solver_id, 3099, task_assignment_id, solved_at, result, fingerprint)
        )

    async def update_complaint(self, complaint_id, updates):
        """
        Update a complaint's information. Prevent updates to the fingerprint column.
        :param complaint_id: The complaint's unique ID (integer).
        :param updates: Dictionary containing the updates (keys are column names).
        """
        # Ensure the fingerprint column cannot be updated
        if "fingerprint" in updates:
            raise ValueError("The 'fingerprint' field cannot be updated.")

        set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
        params = list(updates.values()) + [complaint_id]
        await self.db_manager.update('complaints', set_clause, 'id = ?', params)

    async def get_complaint(self, complaint_id):
        """
        Retrieve a complaint's data by its ID.
        :param complaint_id: The complaint's unique ID (integer).
        :return: Dictionary representing the complaint's data, or None if not found.
        """
        rows = await self.db_manager.read(
            'SELECT * FROM complaints WHERE id = ?',
            (complaint_id,)
        )
        return dict(rows[0]) if rows else None

    async def get_complaints_by_client(self, client_id):
        """
        Retrieve all complaints filed by a specific client.
        :param client_id: The client's unique ID (integer).
        :return: List of dictionaries representing the complaints.
        """
        rows = await self.db_manager.read(
            'SELECT * FROM complaints WHERE client_id = ?',
            (client_id,)
        )
        return [dict(row) for row in rows]

    async def get_complaints_by_solver(self, solver_id):
        """
        Retrieve all complaints involving a specific solver.
        :param solver_id: The solver's unique ID (integer).
        :return: List of dictionaries representing the complaints.
        """
        rows = await self.db_manager.read(
            'SELECT * FROM complaints WHERE solver_id = ?',
            (solver_id,)
        )
        return [dict(row) for row in rows]

    async def delete_complaint(self, complaint_id):
        """
        Delete a complaint by its ID.
        :param complaint_id: The complaint's unique ID (integer).
        """
        await self.db_manager.delete('complaints', 'id = ?', (complaint_id,))
def generate_complaint_fingerprint(client_id, solver_id, created_at, solved_at, result):
    """
    Generate a cryptographically secure fingerprint for the complaint.
    :param client_id: The client's ID (integer or None).
    :param solver_id: The solver's ID (integer).
    :param created_at: The creation timestamp (string).
    :param solved_at: The resolution timestamp (string or None for unsolved).
    :param result: The resolution result (0 or 1).
    :return: Integer representation of the cryptographic fingerprint.
    """
    # Prepare input string
    input_string = f"{client_id or 0}:{solver_id}:{created_at}:{solved_at}:{result}"
    return generate_secure_hash(input_string)

