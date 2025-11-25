# File: app/models/payment.py

from app.extensions import db
from datetime import datetime


class Payment(db.Model):
    """
    Model representing a Payment - Simplified for Pesapal only.
    """

    __tablename__ = "payment"

    paymentId = db.Column(db.Integer, autoincrement=True, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    paymentMethod = db.Column(db.String(100))  # e.g., "Pesapal - M-PESA"
    receiptNumber = db.Column(db.String(100))
    paymentDate = db.Column(db.String(16))  # Format: YYYYMMDDHHMMSS
    purpose = db.Column(db.Enum("Membership", "Event"), nullable=False)
    relatedId = db.Column(db.Integer)  # club_id or event_id
    isManual = db.Column(db.Boolean, default=False)
    status = db.Column(
        db.Enum("Pending", "Completed", "Failed"), default="Pending"
    )
    studentId = db.Column(
        db.Integer,
        db.ForeignKey("students.student_id", ondelete="CASCADE"),
        nullable=False,
    )
    dateCreated = db.Column(db.DateTime, default=datetime.utcnow)
    lastUpdated = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    student = db.relationship("Student", backref="payments")

    def __repr__(self) -> str:
        return f"Payment(paymentId={self.paymentId}, amount={self.amount}, purpose={self.purpose})"

    @classmethod
    def create(cls, details: dict) -> "Payment":
        """
        Create a new Payment record.
        """
        payment = cls(
            amount=details.get("amount"),
            paymentMethod=details.get("paymentMethod"),
            receiptNumber=details.get("receiptNumber"),
            paymentDate=details.get("paymentDate"),
            purpose=details.get("purpose"),
            relatedId=details.get("relatedId"),
            isManual=details.get("isManual", False),
            status=details.get("status", "Pending"),
            studentId=details.get("studentId"),
        )
        db.session.add(payment)
        db.session.commit()
        return payment

    def updateStatus(
        self,
        status: str,
        receipt_number: str = None,
        payment_method: str = None,
    ) -> "Payment":
        """
        Update payment status and related fields.
        """
        self.status = status
        if receipt_number:
            self.receiptNumber = receipt_number
        if payment_method:
            self.paymentMethod = payment_method
        if status == "Completed":
            self.paymentDate = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        db.session.commit()
        return self

    def getDetails(self) -> dict:
        """
        Get payment details as dictionary.
        """
        return {
            "paymentId": self.paymentId,
            "amount": self.amount,
            "paymentMethod": self.paymentMethod,
            "receiptNumber": self.receiptNumber,
            "paymentDate": self.paymentDate,
            "purpose": self.purpose,
            "relatedId": self.relatedId,
            "isManual": self.isManual,
            "status": self.status,
            "studentId": self.studentId,
            "dateCreated": self.dateCreated.isoformat(),
            "lastUpdated": self.lastUpdated.isoformat(),
        }


class PesapalInterimPayment(db.Model):
    """
    Model for tracking interim Pesapal payment processing.
    """

    __tablename__ = "pesapal_interim_payment"

    interimPaymentId = db.Column(
        db.Integer, autoincrement=True, primary_key=True
    )
    paymentId = db.Column(
        db.Integer,
        db.ForeignKey("payment.paymentId", ondelete="CASCADE"),
        nullable=False,
    )
    orderTrackingId = db.Column(db.String(255), nullable=False, unique=True)
    merchantReference = db.Column(db.String(255), nullable=False)
    iframeSrc = db.Column(db.Text, nullable=False)
    status = db.Column(db.Enum("SAVED", "COMPLETED", "FAILED"), default="SAVED")
    dateCreated = db.Column(db.DateTime, default=datetime.utcnow)
    lastUpdated = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    payment = db.relationship("Payment", backref="interim_payment")

    def __repr__(self) -> str:
        return f"PesapalInterimPayment(interimPaymentId={self.interimPaymentId}, orderTrackingId={self.orderTrackingId})"

    @classmethod
    def create(cls, details: dict) -> "PesapalInterimPayment":
        """
        Create a new interim payment record.
        """
        interim_payment = cls(
            paymentId=details.get("paymentId"),
            orderTrackingId=details.get("orderTrackingId"),
            merchantReference=details.get("merchantReference"),
            iframeSrc=details.get("iframeSrc"),
            status=details.get("status", "SAVED"),
        )
        db.session.add(interim_payment)
        db.session.commit()
        return interim_payment

    def updateStatus(self, status: str) -> "PesapalInterimPayment":
        """
        Update interim payment status.
        """
        self.status = status
        db.session.commit()
        return self
