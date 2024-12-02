from app.helpers.process_message import process_message
import re

# Pre-compile regex pattern for optimal performance
FN_PATTERN = re.compile(r"\{fn:([a-fA-F0-9]{64})\}")


import re

# Pre-compile regex pattern for {fn:64-character-hex}
FN_PATTERN = re.compile(r'\{fn:([a-fA-F0-9]{64})\}')

async def validate_handshake(handshake_message):
    """
    Optimized handshake validation with pre-compiled regex.
    Returns:
        str: The fn value (hash) if found
        None: If validation fails or fn not found
    """
    try:
        # Log input message for debugging
        print(f"Received handshake_message: {handshake_message}")

        # Process the message
        res = process_message(handshake_message)
        if not res:
            print("process_message returned None or an invalid response.")
            return None

        print(f"Processed message: {res}")

        # Search for the fn pattern in the processed message
        fn_match = FN_PATTERN.search(res)
        if fn_match:
            print(f"Match found: {fn_match.group(1)}")
            return fn_match.group(1)

        print("No match found in the processed message.")
        return None

    except Exception as e:
        print(f"Handshake failed: {str(e)}")
        return None


async def validate_client_ip(client_info):
    """Validate the client's information."""
    if isinstance(client_info, tuple) and len(client_info) == 2:
        client_ip, client_port = client_info
        if client_ip and client_port:
            print(f"Client {client_ip}:{client_port} is valid.")
            return f"{client_ip}:{client_port}"
    print("Invalid client IP. Closing the connection.")
    return None
