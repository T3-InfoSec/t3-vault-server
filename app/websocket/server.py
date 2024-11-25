import asyncio
from websockets.server import serve
from app.websocket.ws_client_handler import handle_client



async def start_ws_server():
    """Starts the WebSocket server."""
    # Listens for incoming connections from clients (Alice's)
    host = "localhost"
    port = 8080
    print(f"Starting server on ws://{host}:{port}")

    async with serve(handle_client, host, port):
        await asyncio.Future()
