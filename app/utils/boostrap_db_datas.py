from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.database.models.payments import Currency, PaymentMethod, PaymentReason


def bootstrap_data(session: Session):
    try:
        # Check and add Currency
        if not session.query(Currency).filter_by(name="SAT").first():
            satoshi = Currency(name="SAT", currently_accepted=True)
            session.add(satoshi)

        # Check and add Payment Method
        if not session.query(PaymentMethod).filter_by(name="Lightning").first():
            lightning = PaymentMethod(name="Lightning", currently_accepted=True)
            session.add(lightning)

        # Check and add Payment Reasons
         

        reasons = ["SOLVER_SIGNUP", "CLIENT_SIGNUP", "TLP_PAYMENT"]
        existing_reasons = session.query(PaymentReason.description).filter(
            PaymentReason.description.in_(reasons)
        ).all()
        existing_reason_descriptions = {reason[0] for reason in existing_reasons}

        for reason in reasons:
            if reason not in existing_reason_descriptions:
                session.add(PaymentReason(description=reason))

        # Commit the changes
        session.commit()
        print("Bootstrap data successfully added or already exists.")
    except SQLAlchemyError as e:
        session.rollback()
        print(f"An error occurred during bootstrapping: {e}")
