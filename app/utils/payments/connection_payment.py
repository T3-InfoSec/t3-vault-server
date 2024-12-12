from app.utils.fingerprint import Fingerprint
from app.utils.payments.payment_handlers import handle_ln_payment, handle_monero_payment
from enum import Enum

class ConnectorType(Enum):
    CLIENT = "Client"
    SOLVER = "Solver"

class PaymentType(Enum):
    LN = "Lightning"
    MONERO = "Monero"


def pay_for_connection(connector_id: bytes, connector_type: ConnectorType, payment_type: PaymentType = PaymentType.LN):
    try:
        # Convert connector_id to fingerprint in hex
        fingerprint_hex = Fingerprint.fingerprint_to_hex(connector_id)
        
        # Validate connector_type
        if not isinstance(connector_type, ConnectorType):
            raise ValueError(f"Invalid connector type: {connector_type}. Must be one of {[e.value for e in ConnectorType]}")
        
        print(f"Initializing Payment for {connector_type.value} with ID: {fingerprint_hex}")
        print(f"Payment Type: {payment_type.value}")
        
        # Payment handler logic
        if payment_type == PaymentType.LN:
            handle_ln_payment(fingerprint_hex)
        elif payment_type == PaymentType.MONERO:
            handle_monero_payment(fingerprint_hex)
        else:
            raise ValueError(f"Unsupported payment type: {payment_type}.")
    except Exception as e:
        print(f"Error occurred: {e}")
