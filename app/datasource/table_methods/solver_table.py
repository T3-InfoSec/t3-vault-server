from app.datasource.helpers.hash_helper import generate_secure_hash


class SolverTableManager:
    def __init__(self, db_manager):
        """
        Initialize the SolverTableManager with a database manager.
        :param db_manager: Instance of AsyncDatabaseManager for database operations.
        """
        self.db_manager = db_manager

    async def create_table(self):
        """
        Create the 'solvers' table with the specified schema if it doesn't exist.
        """
        schema = """
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT DEFAULT (DATETIME('now')),
        fingerprint INTEGER UNIQUE NOT NULL,
        tasks_taken INTEGER DEFAULT 0,
        tasks_delivered INTEGER DEFAULT 0,
        tasks_expired INTEGER DEFAULT 0,
        tasks_not_complained_about INTEGER DEFAULT 0,
        tasks_complained_about INTEGER DEFAULT 0,
        complaints_won INTEGER DEFAULT 0,
        success_rate FLOAT DEFAULT 0.0,
        computation_power_score FLOAT DEFAULT 0.0,
        reputation_score FLOAT DEFAULT 0.0,
        micropayment INTEGER DEFAULT NULL
        """
        await self.db_manager.create_table('solvers', schema)
    async def add_or_update_solver(self, fingerprint_input, **fields):
        """
        Add a new solver or update existing fields (except 'fingerprint') if the solver exists.
        :param fingerprint: The unique fingerprint of the solver (integer).
        :param fields: Additional fields to insert or update.
        """
        fingerprint = generate_secure_hash(fingerprint_input)

        existing_solver = await self.get_solver_by_fingerprint(fingerprint)

        if existing_solver:
            # Update existing solver (excluding fingerprint)
            updates = {key: value for key, value in fields.items() if key != "fingerprint"}
            if updates:
                set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
                params = list(updates.values()) + [fingerprint]
                query = f"UPDATE solvers SET {set_clause} WHERE fingerprint = ?"
                await self.db_manager.custom_query(query, params)
        else:
            # Insert a new solver
            columns = ", ".join(["fingerprint"] + list(fields.keys()))
            placeholders = ", ".join(["?"] * (len(fields) + 1))
            values = [fingerprint] + list(fields.values())
            query = f"INSERT INTO solvers ({columns}) VALUES ({placeholders})"
            await self.db_manager.custom_query(query, values)

    async def get_solver_by_id(self, solver_id):
        """
        Retrieve a solver's data by their ID.
        :param solver_id: The solver's unique DB key (integer).
        :return: Dictionary representing the solver's data, or None if not found.
        """
        rows = await self.db_manager.read(
            'SELECT * FROM solvers WHERE id = ?',
            (solver_id,)
        )
        return dict(rows[0]) if rows else None

    async def get_solver_by_fingerprint(self, fingerprint):
        """
        Retrieve a solver's data by their fingerprint.
        :param fingerprint: The solver's unique fingerprint (integer).
        :return: Dictionary representing the solver's data, or None if not found.
        """
        rows = await self.db_manager.read(
            'SELECT * FROM solvers WHERE fingerprint = ?',
            (fingerprint,)
        )
        return dict(rows[0]) if rows else None

    async def update_solver(self, solver_id, updates):
        """
        Update a solver's information. Prevent updates to the fingerprint column.
        :param solver_id: The solver's unique DB key (integer).
        :param updates: Dictionary containing the updates (keys are column names).
        """
        if "fingerprint" in updates:
            raise ValueError("The 'fingerprint' field cannot be updated.")

        set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
        params = list(updates.values()) + [solver_id]
        await self.db_manager.update('solvers', set_clause, 'id = ?', params)

    async def delete_solver(self, solver_id):
        """
        Delete a solver by their ID.
        :param solver_id: The solver's unique DB key (integer).
        """
        await self.db_manager.delete('solvers', 'id = ?', (solver_id,))
