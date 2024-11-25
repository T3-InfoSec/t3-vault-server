

import asyncio

from app.websocket.server import start_ws_server


async def main():
    """Main function to start the WebSocket server."""
    await start_ws_server()



if __name__ == "__main__":
    asyncio.run(main())
