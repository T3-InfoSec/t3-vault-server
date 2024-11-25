from app.helpers.process_message import process_message


async def validate_handshake(handshake_message):
    """Validate the handshake message."""
    res = process_message(handshake_message)
    if res == "handshake_response":
        print("Handshake successful.")
        return True
    else:
        print("Handshake failed. Closing the connection.")
        return False


async def validate_client_ip(client_info):
    """Validate the client's information."""
    if isinstance(client_info, tuple) and len(client_info) == 2:
        client_ip, client_port = client_info
        if client_ip and client_port:
            print(f"Client {client_ip}:{client_port} is valid.")
            return f"{client_ip}:{client_port}"
    print("Invalid client IP. Closing the connection.")
    return None
