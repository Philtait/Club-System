# File: app/utils/email.py

from flask import current_app, url_for
from flask_mail import Message
from app.extensions import mail
from app import s
import logging

logger = logging.getLogger(__name__)


def send_email(to, subject, template, **kwargs):
    """Send an email with error handling."""
    try:
        if not current_app.config.get("MAIL_USERNAME"):
            logger.warning("Email service not configured")
            return False

        msg = Message(
            subject=subject,
            recipients=[to] if isinstance(to, str) else to,
            html=template,
            sender=current_app.config["MAIL_DEFAULT_SENDER"],
        )
        mail.send(msg)
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False


def send_confirmation_email(user):
    """Send email confirmation."""
    try:
        token = s.dumps(user.email, salt="email-confirm")
        confirm_url = url_for("auth.confirm_email", token=token, _external=True)

        html = f"""
        <h2>Welcome to Club Management System!</h2>
        <p>Hello {user.first_name},</p>
        <p>Please click the link below to confirm your email address:</p>
        <p><a href="{confirm_url}">Confirm Email</a></p>
        <p>This link will expire in 1 hour.</p>
        """

        return send_email(
            to=user.email, subject="Confirm Your Email Address", template=html
        )
    except Exception as e:
        logger.error(f"Error sending confirmation email: {e}")
        return False


def send_reset_email(user):
    """Send password reset email."""
    try:
        token = s.dumps(user.email, salt="password-reset")
        reset_url = url_for("auth.reset_token", token=token, _external=True)

        html = f"""
        <h2>Password Reset Request</h2>
        <p>Hello {user.first_name},</p>
        <p>Click the link below to reset your password:</p>
        <p><a href="{reset_url}">Reset Password</a></p>
        <p>This link will expire in 1 hour.</p>
        <p>If you did not request this reset, please ignore this email.</p>
        """

        return send_email(
            to=user.email, subject="Password Reset Request", template=html
        )
    except Exception as e:
        logger.error(f"Error sending reset email: {e}")
        return False


def send_membership_request_email(user, club, recipient_emails):
    """Send membership request notification to club leaders."""
    try:
        html = f"""
        <h2>New Membership Request</h2>
        <p>A new membership request has been received:</p>
        <ul>
            <li><strong>Student:</strong> {user.first_name} {user.last_name}</li>
            <li><strong>Email:</strong> {user.email}</li>
            <li><strong>Club:</strong> {club.name}</li>
        </ul>
        <p>Please log in to the system to review and approve/reject this request.</p>
        """

        return send_email(
            to=recipient_emails,
            subject=f"New Membership Request for {club.name}",
            template=html,
        )
    except Exception as e:
        logger.error(f"Error sending membership request email: {e}")
        return False


def send_membership_approved_email(user, club):
    """Send membership approval notification."""
    try:
        html = f"""
        <h2>Membership Approved!</h2>
        <p>Hello {user.first_name},</p>
        <p>Congratulations! Your membership request for <strong>{club.name}</strong> has been approved.</p>
        <p>You can now access all club activities and events.</p>
        <p>Welcome to the club!</p>
        """

        return send_email(
            to=user.email,
            subject=f"Membership Approved - {club.name}",
            template=html,
        )
    except Exception as e:
        logger.error(f"Error sending membership approved email: {e}")
        return False


def send_membership_rejected_email(user, club):
    """Send membership rejection notification."""
    try:
        html = f"""
        <h2>Membership Request Update</h2>
        <p>Hello {user.first_name},</p>
        <p>We regret to inform you that your membership request for <strong>{club.name}</strong> was not approved at this time.</p>
        <p>You may reapply in the future or contact the club leaders for more information.</p>
        """

        return send_email(
            to=user.email,
            subject=f"Membership Request Update - {club.name}",
            template=html,
        )
    except Exception as e:
        logger.error(f"Error sending membership rejected email: {e}")
        return False


def send_event_registration_email(user, event, recipient_emails):
    """Send event registration notification to club administrators."""
    try:
        html = f"""
        <h2>New Event Registration</h2>
        <p>A new event registration has been received:</p>
        <ul>
            <li><strong>Student:</strong> {user.first_name} {user.last_name}</li>
            <li><strong>Email:</strong> {user.email}</li>
            <li><strong>Event:</strong> {event.title}</li>
            <li><strong>Event Date:</strong> {event.event_date.strftime('%Y-%m-%d %H:%M')}</li>
        </ul>
        """

        return send_email(
            to=recipient_emails,
            subject=f"New Registration for {event.title}",
            template=html,
        )
    except Exception as e:
        logger.error(f"Error sending event registration email: {e}")
        return False


def send_event_created_email(event, recipient_emails):
    """Send new event notification to club members."""
    try:
        html = f"""
        <h2>New Event: {event.title}</h2>
        <p>A new event has been scheduled for your club:</p>
        <ul>
            <li><strong>Event:</strong> {event.title}</li>
            <li><strong>Date:</strong> {event.event_date.strftime('%Y-%m-%d %H:%M')}</li>
            <li><strong>Location:</strong> {event.location}</li>
            <li><strong>Description:</strong> {event.description}</li>
        </ul>
        <p>Log in to the system to register for this event.</p>
        """

        return send_email(
            to=recipient_emails,
            subject=f"New Event: {event.title}",
            template=html,
        )
    except Exception as e:
        logger.error(f"Error sending event created email: {e}")
        return False


def send_payment_receipt_email(user, payment):
    """Send payment receipt email."""
    try:
        html = f"""
        <h2>Payment Receipt</h2>
        <p>Hello {user.first_name},</p>
        <p>Your payment has been successfully processed:</p>
        <ul>
            <li><strong>Transaction Code:</strong> {getattr(payment, 'transaction_code', 'N/A')}</li>
            <li><strong>Amount:</strong> KES {payment.amount}</li>
            <li><strong>Purpose:</strong> {payment.purpose}</li>
            <li><strong>Status:</strong> {getattr(payment, 'status', getattr(payment, 'payment_status', 'Unknown'))}</li>
        </ul>
        <p>Thank you for your payment!</p>
        """

        return send_email(
            to=user.email, subject="Payment Receipt", template=html
        )
    except Exception as e:
        logger.error(f"Error sending payment receipt email: {e}")
        return False
