import aiosqlite
import asyncio

from app.datasource.helpers.initialise_db import InitialiseDatabase


class AsyncDatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None

    async def connect(self):
        """
        Establishes a connection to the SQLite database and enables WAL mode for concurrency.
        """
        if self.conn is None:
            self.conn = await aiosqlite.connect(self.db_path)
            self.conn.row_factory = aiosqlite.Row
            await self.conn.execute("PRAGMA journal_mode=WAL;")

    async def get_connection(self):
        """
        Returns the current database connection, initializing it if necessary.
        """
        if self.conn is None:
            await self.connect()
        return self.conn

    async def close(self):
        """
        Closes the database connection.
        """
        if self.conn:
            await self.conn.close()
            self.conn = None

    async def execute_query(self, query, params=None, retries=5, delay=0.5):
        """
        Executes a SQL query with retry logic for handling locked database errors.
        :param query: SQL query string
        :param params: Optional parameters for the query
        :param retries: Number of retries for the query
        :param delay: Delay between retries
        """
        for attempt in range(retries):
            try:
                conn = await self.get_connection()
                async with conn.cursor() as cursor:
                    if params:
                        await cursor.execute(query, params)
                    else:
                        await cursor.execute(query)
                await conn.commit()
                return
            except aiosqlite.OperationalError as e:
                if "database is locked" in str(e) and attempt < retries - 1:
                    await asyncio.sleep(delay)
                else:
                    raise

    async def fetch_query(self, query, params=None):
        """
        Executes a SELECT query and returns the results.
        :param query: SQL SELECT query string
        :param params: Optional parameters for the query
        :return: List of rows
        """
        conn = await self.get_connection()
        async with conn.cursor() as cursor:
            if params:
                await cursor.execute(query, params)
            else:
                await cursor.execute(query)
            return await cursor.fetchall()

    async def create_table(self, table_name, columns):
        """
        Creates a table if it does not already exist.
        :param table_name: Name of the table
        :param columns: Columns definition, e.g., "id INTEGER PRIMARY KEY, name TEXT"
        """
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})"
        await self.execute_query(query)

    async def insert(self, table_name, values):
        """
        Inserts a row into a table.
        :param table_name: Name of the table
        :param values: Tuple of values to insert, e.g., (1, 'Alice')
        """
        placeholders = ", ".join(["?"] * len(values))
        query = f"INSERT INTO {table_name} VALUES ({placeholders})"
        await self.execute_query(query, values)

    async def read(self, query, params=None):
        """
        Executes a SELECT query and returns the results.
        :param query: SQL query string
        :param params: Optional parameters for the query
        :return: List of rows
        """
        return await self.fetch_query(query, params)

    async def update(self, table_name, set_clause, condition, params):
        """
        Updates rows in a table.
        :param table_name: Name of the table
        :param set_clause: SET clause, e.g., "name = ?"
        :param condition: WHERE clause, e.g., "id = ?"
        :param params: Tuple of parameters, e.g., ('Bob', 1)
        """
        query = f"UPDATE {table_name} SET {set_clause} WHERE {condition}"
        await self.execute_query(query, params)

    async def delete(self, table_name, condition, params):
        """
        Deletes rows from a table.
        :param table_name: Name of the table
        :param condition: WHERE clause, e.g., "id = ?"
        :param params: Tuple of parameters, e.g., (1,)
        """
        query = f"DELETE FROM {table_name} WHERE {condition}"
        await self.execute_query(query, params)

    async def custom_query(self, query, params=None):
        """
        Executes a custom SQL query.
        :param query: SQL query string
        :param params: Optional parameters for the query
        :return: List of rows
        """
        return await self.execute_query(query, params)


db_path = "data/t3.db"
db_manager = AsyncDatabaseManager(db_path)


async def startDb():
    await db_manager.get_connection()
    database_initializer = InitialiseDatabase(db_manager)
    await database_initializer.initialize_database()

