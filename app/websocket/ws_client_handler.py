import asyncio

from websockets import ConnectionClosedOK
from app.helpers.process_message import process_message
from app.websocket.client import connect_ws_client
from app.websocket.ws_client_validation import validate_client_ip, validate_handshake


async def handle_client(websocket, path):
    """Handles communication with a single client."""
    client_info = websocket.remote_address
    client_details = await validate_client_ip(client_info)
    if client_details is None:
        await websocket.close(reason="Client IP validation failed")

        return

    print(f"Client connected: {client_details}")

    try:
        await websocket.send(
            f"Hello from server! You are connected as {client_details}. Please send a valid handshake message to continue."
        )
        try:
            handshake_message = await asyncio.wait_for(websocket.recv(), timeout=30)
            print(
                f"Received handshake message from {client_details}: {handshake_message}"
            )
            if not await validate_handshake(handshake_message):
                await websocket.send("Invalid handshake. Closing the connection.")
                await websocket.close(reason="Invalid handshake")
                print(f"Client {client_details} disconnected due to invalid handshake")
                return

        except asyncio.TimeoutError:
            print(
                f"No handshake message received from {client_details} within 30 seconds."
            )
            await websocket.send("Timeout. Closing the connection.")
            await websocket.close(reason="Timeout")
            return

        async for message in websocket:
            processed_message = process_message(message)
            if processed_message is None:
                await websocket.send("Invalid TLP message. Closing the connection.")
                await websocket.close(reason="Invalid TLP message")
                print(
                    f"Client {client_details} disconnected due to invalid TLP message"
                )
                return

            print(f"Received message from {client_details}: {processed_message}")
            await websocket.send(
                "TLP is being processed. You will receive a response once TLP is done."
            )
            print(f"Sending message to processor server: {processed_message}")
            # send message to processor server
            response_from_patrick = await connect_ws_client(message=processed_message)
            print(f"Received response from processor server: {response_from_patrick}")
            #
            await websocket.send(response_from_patrick)

            #
    except ConnectionClosedOK:
        print(f"Client {client_details} disconnected")
    except Exception as e:
        print(f"Error with client {client_details}: {e}")
