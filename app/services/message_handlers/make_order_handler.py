from sqlalchemy.orm import Session
from sqlalchemy.sql import and_

from app.database.models.booking import Booking
from app.database.models.provider import Provider
from app.database.models.order import Order
from app.utils.encryption import Encryption


def auto_match_booking(
    client_id: str, session: Session, price: float, min_reputation: float = 0.0
):
    """
    Auto-matches a booking to a provider based on an exact price match and reputation.
    Creates an order for the client if a match is found.

    Args:
        client_id (str): The ID of the client creating the booking.
        session (Session): SQLAlchemy session.
        price (float): The exact price for which the booking must match.
        min_reputation (float): The minimum reputation threshold for providers (default is 0.0).

    Returns:
        str: Match status message.
    """
    # Find the first booking matching the exact price
    booking = (
        session.query(Booking)
        .filter(
            and_(
                Booking.price == price,
                Booking.status == "pending",
            )
        )
        .order_by(Booking.created_at.asc())
        .first()
    )

    if not booking:
        return f"No booking found with the exact price {price}."

    # Find a provider meeting the reputation criteria
    matching_provider = (
        session.query(Provider)
        .filter(
            and_(
                Provider.reputation_score >= min_reputation,
                Provider.reputation_score > 0,
            )
        )
        .order_by(Provider.reputation_score.desc())
        .first()
    )

    if matching_provider:
        # Create an order for the client
        enc = Encryption()
        client_id_f = enc.generate_fingerprint(client_id)

        new_order = Order(
            booking_id=booking.db_key,
            client_id=client_id_f,
            started_at=None,
            status="in-progress",
        )

        session.add(new_order)
        session.commit()

        return (
            f"Booking {booking.db_key} matched with provider {matching_provider.db_key} "
            f"(Reputation: {matching_provider.reputation_score}, Price: {booking.price}). "
            f"Order {new_order.id} created for client {client_id}."
        )
    else:
        return f"No suitable provider found for bookings priced at {price} with reputation >= {min_reputation}."
