class ClientTableManager:
    def __init__(self, db_manager):
        """
        Initialize the ClientTableManager with a database manager.
        :param db_manager: Instance of AsyncDatabaseManager for database operations.
        """
        self.db_manager = db_manager

    async def create_table(self):
        """
        Create the 'clients' table with the specified schema if it doesn't exist.
        The 'created_at' column is automatically set to the current date and time.
        """
        schema = """
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT DEFAULT (DATETIME('now')),
        fingerprint INTEGER,
        tasks_history TEXT,
        tasks_requested INTEGER DEFAULT 0,
        tasks_received INTEGER DEFAULT 0,
        tasks_complained INTEGER DEFAULT 0,
        tasks_accepted INTEGER DEFAULT 0,
        acceptance_rate FLOAT DEFAULT 0.0,
        reputation FLOAT DEFAULT 0.0
        """
        await self.db_manager.create_table('clients', schema)

    async def add_client(self, fingerprint=None, tasks_history=""):
        """
        Add a new client to the database.
        The 'created_at' column is automatically set to the current timestamp.
        :param fingerprint: The client's fingerprint (integer). Defaults to None for anonymous clients.
        :param tasks_history: Initial tasks history (default: empty string).
        """
        await self.db_manager.insert(
            'clients',
            (None, None if fingerprint is None else fingerprint, tasks_history, 0, 0, 0, 0, 0.0, 0.0)
        )

    async def update_client_stats(self, fingerprint, stats):
        """
        Update a client's statistics.
        :param fingerprint: The client's fingerprint (integer).
        :param stats: Dictionary containing the stats to update (keys are column names).
        """
        set_clause = ", ".join([f"{key} = ?" for key in stats.keys()])
        params = list(stats.values()) + [fingerprint]
        await self.db_manager.update('clients', set_clause, 'fingerprint = ?', params)

    async def get_client(self, fingerprint):
        """
        Retrieve a client's data by fingerprint.
        :param fingerprint: The client's fingerprint (integer).
        :return: Dictionary representing the client's data, or None if not found.
        """
        rows = await self.db_manager.read(
            'SELECT * FROM clients WHERE fingerprint IS ?',
            (fingerprint,)
        )
        return dict(rows[0]) if rows else None

    async def delete_client_by_id(self, id):
        """
        Delete a client by id.
        :param id: The client's unique database ID (integer).
        """
        await self.db_manager.delete('clients', 'id = ?', (id,))

    async def delete_client_by_fingerprint(self, fingerprint):
        """
        Delete a client by fingerprint.
        :param fingerprint: The client's fingerprint (integer).
        """
        await self.db_manager.delete('clients', 'fingerprint IS ?', (fingerprint,))
