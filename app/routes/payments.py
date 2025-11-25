# File: app/routes/payments.py (Updated - Replace existing)

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    jsonify,
    current_app,
)
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime

from app.extensions import db
from app.models import (
    Payment,
    PesapalInterimPayment,
    Membership,
    Club,
    Event,
)
from app.utils import pesapal

payments_bp = Blueprint("payments", __name__, url_prefix="/payments")


def student_required(f):
    """Decorator to ensure the current_user is a Student with a valid student record."""

    @wraps(f)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("auth.login"))

        if current_user.role != "Student":
            flash("Only students can access this page.", "warning")
            return redirect(url_for("dashboard.dashboard"))

        if not current_user.student:
            flash("Student profile not found. Please contact support.", "error")
            return redirect(url_for("dashboard.dashboard"))

        return f(*args, **kwargs)

    return decorated_view


def admin_required(f):
    """Decorator to ensure the current_user is an Admin."""

    @wraps(f)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "Admin":
            flash("Access denied – Admins only.", "warning")
            return redirect(url_for("dashboard.dashboard"))
        return f(*args, **kwargs)

    return decorated_view


# === PAYMENT INITIATION ROUTES ===


@payments_bp.route("/membership")
@login_required
@student_required
def membership_payment():
    """Show membership payment page."""
    memberships = Membership.query.filter_by(
        student_id=current_user.student.student_id,
        left_on=None,
        status="Approved",
    ).all()

    return render_template(
        "payments/membership_payment.html", memberships=memberships
    )


@payments_bp.route("/event/<int:event_id>")
@login_required
@student_required
def event_payment(event_id):
    """Show event payment page."""
    event = Event.query.get_or_404(event_id)
    return render_template("payments/event_payment.html", event=event)


@payments_bp.route("/initiate", methods=["POST"])
@login_required
@student_required
def initiate_payment():
    """Initiate Pesapal payment - unified endpoint."""
    try:
        data = request.get_json()
        purpose = data.get("purpose")  # 'Membership' or 'Event'
        related_id = data.get("related_id")  # club_id or event_id
        amount = float(data.get("amount"))
        customer_name = data.get(
            "customer_name",
            f"{current_user.first_name} {current_user.last_name}",
        )
        phone_number = data.get("phone_number")

        current_app.logger.info(f"💳 Payment initiation request: {data}")

        # Validate input
        if not all([purpose, related_id, amount, phone_number]):
            return (
                jsonify({"success": False, "error": "Missing required fields"}),
                400,
            )

        # Validate purpose and related object exists
        if purpose == "Membership":
            club = Club.query.get(related_id)
            if not club:
                return (
                    jsonify({"success": False, "error": "Club not found"}),
                    404,
                )
            description = f"Membership payment for {club.name}"
        elif purpose == "Event":
            event = Event.query.get(related_id)
            if not event:
                return (
                    jsonify({"success": False, "error": "Event not found"}),
                    404,
                )
            description = f"Event registration payment for {event.title}"
        else:
            return jsonify({"success": False, "error": "Invalid purpose"}), 400

        # Create payment record
        payment = Payment.create(
            {
                "studentId": current_user.student.student_id,
                "amount": amount,
                "purpose": purpose,
                "relatedId": related_id,
                "status": "Pending",
            }
        )

        current_app.logger.info(
            f"💰 Created payment with ID: {payment.paymentId}"
        )

        # Get base URL for callbacks
        base_url = f"{request.scheme}://{request.host}"

        # Get Pesapal access token
        token_response = pesapal.get_access_token()
        access_token = token_response["token"]

        if not access_token:
            raise Exception("Failed to get access token")

        # Register IPN URL
        ipn_url = f"{base_url}/payments/pesapal/ipn"
        notification_response = pesapal.get_notification_id(
            access_token, ipn_url
        )
        notification_id = notification_response["ipn_id"]

        if not notification_id:
            raise Exception("Failed to register IPN")

        # Create merchant reference
        merchant_reference = (
            f"PAYMENT_{payment.paymentId}_{int(datetime.utcnow().timestamp())}"
        )

        # Prepare order details
        order_details = {
            "amount": amount,
            "customer_name": customer_name,
            "phone_number": phone_number,
            "email_address": current_user.email,
            "description": description,
            "merchant_reference": merchant_reference,
            "notification_id": notification_id,
        }

        # Create Pesapal order
        order_response = pesapal.get_merchant_order_url(
            order_details, access_token, base_url
        )

        if not order_response.get("order_tracking_id"):
            raise Exception("Failed to create Pesapal order")

        # Store interim payment record
        PesapalInterimPayment.create(
            {
                "paymentId": payment.paymentId,
                "orderTrackingId": order_response["order_tracking_id"],
                "merchantReference": order_response["merchant_reference"],
                "iframeSrc": order_response["redirect_url"],
                "status": "SAVED",
            }
        )

        current_app.logger.info("✅ Payment initiation successful")

        return jsonify(
            {
                "success": True,
                "payment_id": payment.paymentId,
                "order_tracking_id": order_response["order_tracking_id"],
                "iframe_src": order_response["redirect_url"],
                "message": "Payment initiated successfully",
            }
        )

    except Exception as error:
        db.session.rollback()
        current_app.logger.error(f"❌ Payment initiation error: {error}")
        return jsonify({"success": False, "error": str(error)}), 500


@payments_bp.route("/iframe/<int:payment_id>")
@login_required
@student_required
def payment_iframe(payment_id):
    """Show payment iframe."""
    payment = Payment.query.get_or_404(payment_id)

    # Ensure the payment belongs to the current user
    if payment.studentId != current_user.student.student_id:
        flash("Access denied", "error")
        return redirect(url_for("payments.history"))

    interim_payment = PesapalInterimPayment.query.filter_by(
        paymentId=payment_id
    ).first()
    if not interim_payment:
        flash("Payment session not found", "error")
        return redirect(url_for("payments.history"))

    return render_template(
        "payments/iframe.html",
        payment=payment,
        iframe_src=interim_payment.iframeSrc,
    )


# === PAYMENT CALLBACK AND IPN HANDLING ===


@payments_bp.route("/pesapal/callback")
def pesapal_callback():
    """Handle Pesapal payment callback."""
    try:
        order_tracking_id = request.args.get("OrderTrackingId")
        current_app.logger.info(
            f"🔄 Payment callback received for: {order_tracking_id}"
        )

        if not order_tracking_id:
            flash("Payment tracking ID is missing", "error")
            return redirect(url_for("payments.history"))

        # Get access token
        token_response = pesapal.get_access_token()
        access_token = token_response["token"]

        if not access_token:
            flash("Payment verification failed", "error")
            return redirect(url_for("payments.history"))

        # Check transaction status
        status_response = pesapal.get_transaction_status(
            order_tracking_id, access_token
        )
        payment_status = status_response.get("payment_status_description")

        current_app.logger.info(f"💳 Payment status: {payment_status}")

        # Find the interim payment record
        interim_payment = PesapalInterimPayment.query.filter_by(
            orderTrackingId=order_tracking_id
        ).first()

        if not interim_payment:
            flash("Payment record not found", "error")
            return redirect(url_for("payments.history"))

        payment = interim_payment.payment

        if payment_status == "Completed":
            # Update payment status
            payment.updateStatus(
                status="Completed",
                receipt_number=status_response.get("confirmation_code"),
                payment_method=f"Pesapal - {status_response.get('payment_method', 'Unknown')}",
            )

            # Update interim payment status
            interim_payment.updateStatus("COMPLETED")

            current_app.logger.info("✅ Payment completed successfully")
            flash("Payment completed successfully!", "success")
            return redirect(
                url_for("payments.success", payment_id=payment.paymentId)
            )

        elif payment_status == "Failed":
            # Update payment status
            payment.updateStatus(status="Failed")
            interim_payment.updateStatus("FAILED")

            current_app.logger.info("❌ Payment failed")
            flash("Payment failed. Please try again.", "error")
            return redirect(url_for("payments.history"))
        else:
            current_app.logger.info("⏳ Payment still pending")
            flash("Payment is still being processed. Please wait...", "info")
            return redirect(url_for("payments.history"))

    except Exception as error:
        current_app.logger.error(f"❌ Callback error: {error}")
        flash("An error occurred during payment processing", "error")
        return redirect(url_for("payments.history"))


@payments_bp.route("/pesapal/ipn")
def pesapal_ipn():
    """Handle Pesapal IPN notifications."""
    try:
        order_tracking_id = request.args.get("OrderTrackingId")
        current_app.logger.info(
            f"📢 IPN notification received for: {order_tracking_id}"
        )

        if not order_tracking_id:
            return "Missing OrderTrackingId", 400

        # Get access token
        token_response = pesapal.get_access_token()
        access_token = token_response["token"]

        if not access_token:
            return "Error: Cannot retrieve access token", 400

        # Get transaction status
        status_response = pesapal.get_transaction_status(
            order_tracking_id, access_token
        )
        payment_status = status_response.get("payment_status_description")

        # Find interim payment
        interim_payment = PesapalInterimPayment.query.filter_by(
            orderTrackingId=order_tracking_id
        ).first()

        if not interim_payment:
            current_app.logger.error(
                f"Interim payment not found for: {order_tracking_id}"
            )
            return "Payment record not found", 404

        payment = interim_payment.payment

        if payment_status == "Completed":
            # Update payment status
            payment.updateStatus(
                status="Completed",
                receipt_number=status_response.get("confirmation_code"),
                payment_method=f"Pesapal - {status_response.get('payment_method', 'Unknown')}",
            )
            interim_payment.updateStatus("COMPLETED")

            current_app.logger.info(
                f"✅ IPN: Payment {payment.paymentId} completed"
            )

        elif payment_status == "Failed":
            payment.updateStatus(status="Failed")
            interim_payment.updateStatus("FAILED")

            current_app.logger.info(
                f"❌ IPN: Payment {payment.paymentId} failed"
            )

        return "IPN processed", 200

    except Exception as error:
        current_app.logger.error(f"❌ IPN error: {error}")
        return "IPN processing error", 500


# === PAYMENT STATUS AND HISTORY ===


@payments_bp.route("/success/<int:payment_id>")
@login_required
@student_required
def success(payment_id):
    """Show payment success page."""
    payment = Payment.query.get_or_404(payment_id)

    # Ensure the payment belongs to the current user
    if payment.studentId != current_user.student.student_id:
        flash("Access denied", "error")
        return redirect(url_for("payments.history"))

    return render_template("payments/success.html", payment=payment)


@payments_bp.route("/history")
@login_required
@student_required
def history():
    """Show payment history for current student."""
    payments = (
        Payment.query.filter_by(studentId=current_user.student.student_id)
        .order_by(Payment.dateCreated.desc())
        .all()
    )

    return render_template("payments/history.html", payments=payments)


@payments_bp.route("/api/status/<int:payment_id>")
@login_required
@student_required
def api_payment_status(payment_id):
    """API endpoint to check payment status."""
    payment = Payment.query.get_or_404(payment_id)

    # Ensure the payment belongs to the current user
    if payment.studentId != current_user.student.student_id:
        return jsonify({"error": "Access denied"}), 403

    return jsonify(
        {
            "payment_id": payment.paymentId,
            "status": payment.status,
            "amount": payment.amount,
            "purpose": payment.purpose,
        }
    )


# === ADMIN ROUTES ===


@payments_bp.route("/admin/pending")
@login_required
@admin_required
def admin_pending_payments():
    """Admin view of pending payments."""
    pending_payments = Payment.query.filter_by(status="Pending").all()
    return render_template(
        "payments/admin_pending.html", payments=pending_payments
    )


@payments_bp.route("/admin/all")
@login_required
@admin_required
def admin_all_payments():
    """Admin view of all payments."""
    payments = Payment.query.order_by(Payment.dateCreated.desc()).all()
    return render_template("payments/admin_all.html", payments=payments)


@payments_bp.route("/admin/mark-completed/<int:payment_id>", methods=["POST"])
@login_required
@admin_required
def admin_mark_completed(payment_id):
    """Admin manually mark payment as completed."""
    payment = Payment.query.get_or_404(payment_id)

    payment.updateStatus(
        status="Completed",
        receipt_number=f"MANUAL_{payment_id}",
        payment_method="Manual Override",
    )

    flash(f"Payment {payment_id} marked as completed.", "success")
    return redirect(url_for("payments.admin_pending_payments"))


@payments_bp.route("/admin/mark-failed/<int:payment_id>", methods=["POST"])
@login_required
@admin_required
def admin_mark_failed(payment_id):
    """Admin manually mark payment as failed."""
    payment = Payment.query.get_or_404(payment_id)
    payment.updateStatus(status="Failed")

    flash(f"Payment {payment_id} marked as failed.", "info")
    return redirect(url_for("payments.admin_pending_payments"))
