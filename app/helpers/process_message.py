import json

def process_message(message: str):
    """
    Process the message received from the client.

    Args:
        message (str): The incoming message as a string.

    Returns:
        str | None: Returns "handshake_response" for handshake messages,
                    the original message string for valid JSON messages,
                    or None for invalid JSON messages.
    """
    try:        
        if message.__contains__("fn"):                        
            return message
        json.loads(message)
        return message

    except (json.JSONDecodeError, ValueError):
        return None
    except Exception as e:
        return f"Error processing message: {e}"

# x1Zf0o115HelloTestKey
# {
#     "baseg": 100,
#     "product": 30,
#     "t": 5
# }

# handshake is going to be the public key of bellow
# x1Zf03-(client_device_id[8 chars])-yc