from app.datasource.helpers.hash_helper import generate_secure_hash


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
        fingerprint INTEGER UNIQUE NOT NULL,
        tasks_requested INTEGER DEFAULT 0,
        tasks_received INTEGER DEFAULT 0,
        tasks_complained INTEGER DEFAULT 0,
        tasks_accepted INTEGER DEFAULT 0,
        acceptance_rate FLOAT DEFAULT 0.0,
        reputation FLOAT DEFAULT 0.0,
        micropayment INTEGER DEFAULT NULL
        """
        await self.db_manager.create_table('clients', schema)

    async def add_or_update_client(self, key, **fields):
        """
        Add a new client or update existing fields if the client exists.
        :param fingerprint: The unique fingerprint of the client (integer).
        :param fields: Additional fields to insert or update.
        """
        # up to user to provide same key always or change (for annonymity)
        fingerprint = generate_secure_hash(key)        
        existing_client = await self.get_client_by_fingerprint(fingerprint)

        if existing_client:
            # Update existing client
            updates = {key: value for key, value in fields.items() if key != "fingerprint"}
            if updates:
                set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
                params = list(updates.values()) + [fingerprint]
                await self.db_manager.update('clients', set_clause, 'fingerprint = ?', params)
        else:
            # Add a new client
            columns = ", ".join(["fingerprint"] + list(fields.keys()))
            placeholders = ", ".join(["?"] * (len(fields) + 1))
            values = [fingerprint] + list(fields.values())
            await self.db_manager.insert('clients', columns, placeholders, values)

    async def get_client_by_id(self, client_id):
        """
        Retrieve a client's data by their ID.
        :param client_id: The client's unique DB key (integer).
        :return: Dictionary representing the client's data, or None if not found.
        """
        rows = await self.db_manager.read(
            'SELECT * FROM clients WHERE id = ?',
            (client_id,)
        )
        return dict(rows[0]) if rows else None

    async def get_client_by_fingerprint(self, fingerprint):
        """
        Retrieve a client's data by their fingerprint.
        :param fingerprint: The client's unique fingerprint (integer).
        :return: Dictionary representing the client's data, or None if not found.
        """
        rows = await self.db_manager.read(
            'SELECT * FROM clients WHERE fingerprint = ?',
            (fingerprint,)
        )
        return dict(rows[0]) if rows else None

    async def update_client(self, client_id, updates):
        """
        Update a client's information. Prevent updates to the fingerprint column.
        :param client_id: The client's unique DB key (integer).
        :param updates: Dictionary containing the updates (keys are column names).
        """
        if "fingerprint" in updates:
            raise ValueError("The 'fingerprint' field cannot be updated.")

        set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
        params = list(updates.values()) + [client_id]
        await self.db_manager.update('clients', set_clause, 'id = ?', params)

    async def delete_client(self, client_id):
        """
        Delete a client by their ID.
        :param client_id: The client's unique DB key (integer).
        """
        await self.db_manager.delete('clients', 'id = ?', (client_id,))
