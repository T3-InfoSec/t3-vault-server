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
        fingerprint binary(16) UNIQUE NOT NULL,
        tasks_requested INTEGER DEFAULT 0,
        tasks_received INTEGER DEFAULT 0,
        tasks_complained INTEGER DEFAULT 0,
        tasks_accepted INTEGER DEFAULT 0,
        acceptance_rate FLOAT DEFAULT 0.0,
        reputation FLOAT DEFAULT 0.0,
        micropayment INTEGER DEFAULT 0
        """
        await self.db_manager.create_table('clients', schema)
    async def add_or_update_client_conn(self, key, **fields):
        """
        Add a new client or update the fields of an existing client.
        If the client with the same fingerprint already exists, updates the provided fields.
        If task_requested exists, increments it by 1 during an update.
        
        :param key: The key used to generate the fingerprint.
        :param fields: Additional fields to insert or update.
        """
        fingerprint = key
        existing_client = await self.get_client_by_fingerprint(fingerprint)

        if existing_client:
            print(f"Updating client with fingerprint: {fingerprint}")
            
            # Increment task_requested by 1
            updates = {key: value for key, value in fields.items() if key != "fingerprint"}
            if 'tasks_requested' not in updates:
                updates['tasks_requested'] = existing_client['tasks_requested'] + 1

            set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
            query = f"UPDATE clients SET {set_clause} WHERE fingerprint = ?"
            params = list(updates.values()) + [fingerprint]
            await self.db_manager.custom_query(query, params)
        else:
            # If task_requested is not provided, default to 1 for new entries
            fields['tasks_requested'] = fields.get('tasks_requested', 1)

            columns = ", ".join(["fingerprint"] + list(fields.keys()))
            placeholders = ", ".join(["?"] * (len(fields) + 1))
            query = f"INSERT INTO clients ({columns}) VALUES ({placeholders})"
            params = [fingerprint] + list(fields.values())
            await self.db_manager.custom_query(query, params)

    async def get_client_by_id(self, client_id):
        """
        Retrieve a client's data by their database ID.
        :param client_id: The client's unique database ID (integer).
        :return: Dictionary representing the client's data, or None if not found.
        """
        query = "SELECT * FROM clients WHERE id = ?"
        rows = await self.db_manager.custom_query(query, (client_id,))
        return dict(rows[0]) if rows else None

    async def get_client_by_fingerprint(self, fingerprint):
        """
        Retrieve a client's data by their fingerprint.
        :param fingerprint: The client's unique fingerprint (BIGINT).
        :return: Dictionary representing the client's data, or None if not found.
        """
        query = "SELECT * FROM clients WHERE fingerprint = ?"
        rows = await self.db_manager.read(query, (fingerprint,))
        return dict(rows[0]) if rows else None

    async def update_client(self, client_id, updates):
        """
        Update a client's information by their database ID.
        Prevents updates to the 'fingerprint' column.
        :param client_id: The client's unique database ID (integer).
        :param updates: Dictionary containing the updates (keys are column names).
        """
        if "fingerprint" in updates:
            raise ValueError("The 'fingerprint' field cannot be updated.")

        set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
        query = f"UPDATE clients SET {set_clause} WHERE id = ?"
        params = list(updates.values()) + [client_id]
        await self.db_manager.custom_query(query, params)

    async def delete_client(self, client_id):
        """
        Delete a client from the database using their unique ID.
        :param client_id: The client's unique database ID (integer).
        """
        query = "DELETE FROM clients WHERE id = ?"
        await self.db_manager.custom_query(query, (client_id,))
