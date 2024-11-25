from websockets import connect
from app.helpers.process_message import process_message


async def connect_ws_client(host="localhost", port=8085, message=""):
    """Connects to the WebSocket server, sends a message, and waits for a response."""
    websocket = None
    try:
        async with connect(f"ws://{host}:{port}") as websocket:
            await websocket.send(message)
            response = await websocket.recv()
            return process_message(response)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if websocket:
            await websocket.close()
            print("Server socket closed")
