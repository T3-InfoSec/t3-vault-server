from app.models.alice_tlp_data import AliceTLPData
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
        if message == "x1Zf0o115HelloTestKey":
            return "handshake_response"        
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