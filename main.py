import asyncio

from app.datasource.db import startDb
from app.websocket.server import start_ws_server


async def main():
    """Main function to start the WebSocket server."""
    try:
        await startDb()
        print("Database initialized.")
        await start_ws_server()
        print("WebSocket server started.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print("Main function execution completed.")


if __name__ == "__main__":
    asyncio.run(main())
