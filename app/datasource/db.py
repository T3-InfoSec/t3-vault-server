import aiosqlite
from contextlib import asynccontextmanager

class AsyncDatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None

    async def connect(self):
        if self.conn is None:
            self.conn = await aiosqlite.connect(self.db_path)
            self.conn.row_factory = aiosqlite.Row

    async def get_connection(self):
        if self.conn is None:
            await self.connect()
        return self.conn

    async def close(self):
        if self.conn:
            await self.conn.close()
            self.conn = None

    async def create_table(self, table_name, columns):
        """
        Create a table if it does not already exist.
        :param table_name: Name of the table
        :param columns: Columns definition, e.g., "id INTEGER PRIMARY KEY, name TEXT"
        """
        conn = await self.get_connection()
        async with conn.cursor() as cursor:
            await cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})")
        await conn.commit()

    async def insert(self, table_name, values):
        """
        Insert a row into a table.
        :param table_name: Name of the table
        :param values: Tuple of values to insert, e.g., (1, 'Alice')
        """
        conn = await self.get_connection()
        placeholders = ", ".join(["?"] * len(values))  # Generate placeholders for the values
        query = f"INSERT INTO {table_name} VALUES ({placeholders})"
        async with conn.cursor() as cursor:
            await cursor.execute(query, values)
        await conn.commit()

    async def read(self, query, params=None):
        """
        Execute a SELECT query.
        :param query: SQL query string
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

    async def update(self, table_name, set_clause, condition, params):
        """
        Update rows in a table.
        :param table_name: Name of the table
        :param set_clause: SET clause, e.g., "name = ?"
        :param condition: WHERE clause, e.g., "id = ?"
        :param params: Tuple of parameters, e.g., ('Bob', 1)
        """
        conn = await self.get_connection()
        query = f"UPDATE {table_name} SET {set_clause} WHERE {condition}"
        async with conn.cursor() as cursor:
            await cursor.execute(query, params)
        await conn.commit()

    async def delete(self, table_name, condition, params):
        """
        Delete rows from a table.
        :param table_name: Name of the table
        :param condition: WHERE clause, e.g., "id = ?"
        :param params: Tuple of parameters, e.g., (1,)
        """
        conn = await self.get_connection()
        query = f"DELETE FROM {table_name} WHERE {condition}"
        async with conn.cursor() as cursor:
            await cursor.execute(query, params)
        await conn.commit()



# Example Usage
async def main():
    db_manager = AsyncDatabaseManager('t3.db')
    await db_manager.connect()

    # Create a table
    await db_manager.create_table('users', 'id INTEGER PRIMARY KEY, name TEXT')

    # Insert data
    await db_manager.insert('users', (1, 'Alice'))
    await db_manager.insert('users', (2, 'Bob'))

    # Read data
    rows = await db_manager.read('SELECT * FROM users')
    for row in rows:
        print(dict(row))

    # Update data
    await db_manager.update('users', 'name = ?', 'id = ?', ('Charlie', 2))

    # Read data again
    rows = await db_manager.read('SELECT * FROM users')
    for row in rows:
        print(dict(row))

    # Delete data
    await db_manager.delete('users', 'id = ?', (1,))

    # Read data after deletion
    rows = await db_manager.read('SELECT * FROM users')
    for row in rows:
        print(dict(row))

    # Close the connection
    await db_manager.close()

# Run in an async environment
import asyncio
asyncio.run(main())
