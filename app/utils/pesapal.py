# File: app/utils/pesapal.py

import os
import requests
import logging

logger = logging.getLogger(__name__)

# Pesapal API endpoints
PESAPAL_BASE_URL = "https://cybqa.pesapal.com/pesapalv3/api"  # Sandbox URL
TOKEN_ENDPOINT = f"{PESAPAL_BASE_URL}/Auth/RequestToken"
REGISTER_IPN_ENDPOINT = f"{PESAPAL_BASE_URL}/URLSetup/RegisterIPN"
SUBMIT_ORDER_ENDPOINT = f"{PESAPAL_BASE_URL}/Transactions/SubmitOrderRequest"
TRANSACTION_STATUS_ENDPOINT = (
    f"{PESAPAL_BASE_URL}/Transactions/GetTransactionStatus"
)


def split_full_name(full_name):
    """Split full name into first, middle, and last names."""
    name_parts = full_name.split()

    if len(name_parts) == 2:
        first_name, last_name = name_parts
        middle_name = ""
    elif len(name_parts) > 2:
        first_name = name_parts[0]
        middle_name = " ".join(name_parts[1:-1])
        last_name = name_parts[-1]
    else:
        first_name = full_name
        middle_name = last_name = ""

    return first_name, middle_name, last_name


def get_access_token():
    """Get Pesapal access token."""
    try:
        consumer_key = os.getenv(
            "PESAPAL_CONSUMER_KEY", "qkio1BGGYAXTu2JOfm7XSXNruoZsrqEW"
        )
        consumer_secret = os.getenv(
            "PESAPAL_CONSUMER_SECRET", "osGQ364R49cXKeOYSpaOnT++rHs="
        )

        if not consumer_key or not consumer_secret:
            logger.error("Pesapal credentials not configured")
            return {"token": None, "error": "Credentials not configured"}

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        data = {
            "consumer_key": consumer_key,
            "consumer_secret": consumer_secret,
        }

        response = requests.post(
            TOKEN_ENDPOINT, json=data, headers=headers, timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            return {"token": result.get("token"), "error": None}
        else:
            logger.error(
                f"Failed to get access token: {response.status_code} - {response.text}"
            )
            return {"token": None, "error": f"HTTP {response.status_code}"}

    except requests.exceptions.Timeout:
        logger.error("Timeout while getting access token")
        return {"token": None, "error": "Request timeout"}
    except Exception as e:
        logger.error(f"Error getting access token: {e}")
        return {"token": None, "error": str(e)}


def get_notification_id(access_token, ipn_url):
    """Register IPN URL and get notification ID."""
    try:
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
        }

        data = {"url": ipn_url, "ipn_notification_type": "GET"}

        response = requests.post(
            REGISTER_IPN_ENDPOINT, json=data, headers=headers, timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            return {"ipn_id": result.get("ipn_id"), "error": None}
        else:
            logger.error(
                f"Failed to register IPN: {response.status_code} - {response.text}"
            )
            return {"ipn_id": None, "error": f"HTTP {response.status_code}"}

    except requests.exceptions.Timeout:
        logger.error("Timeout while registering IPN")
        return {"ipn_id": None, "error": "Request timeout"}
    except Exception as e:
        logger.error(f"Error registering IPN: {e}")
        return {"ipn_id": None, "error": str(e)}


def get_merchant_order_url(order_details, access_token, base_url):
    """Submit order and get redirect URL."""
    try:
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
        }

        # Split customer name
        first_name, middle_name, last_name = split_full_name(
            order_details["customer_name"]
        )

        # Build the order request
        order_request = {
            "id": order_details["merchant_reference"],
            "currency": "KES",
            "amount": float(order_details["amount"]),
            "description": order_details["description"],
            "callback_url": f"{base_url}/payments/pesapal/callback",
            "notification_id": order_details["notification_id"],
            "billing_address": {
                "phone_number": order_details["phone_number"],
                "email_address": order_details.get("email_address", ""),
                "country_code": "KE",
                "first_name": first_name,
                "middle_name": middle_name,
                "last_name": last_name,
                "line_1": "",
                "line_2": "",
                "city": "",
                "state": "",
                "postal_code": "",
                "zip_code": "",
            },
        }

        response = requests.post(
            SUBMIT_ORDER_ENDPOINT,
            json=order_request,
            headers=headers,
            timeout=30,
        )

        if response.status_code == 200:
            result = response.json()
            return {
                "order_tracking_id": result.get("order_tracking_id"),
                "merchant_reference": result.get("merchant_reference"),
                "redirect_url": result.get("redirect_url"),
                "error": None,
            }
        else:
            logger.error(
                f"Failed to submit order: {response.status_code} - {response.text}"
            )
            return {
                "order_tracking_id": None,
                "merchant_reference": None,
                "redirect_url": None,
                "error": f"HTTP {response.status_code}",
            }

    except requests.exceptions.Timeout:
        logger.error("Timeout while submitting order")
        return {
            "order_tracking_id": None,
            "merchant_reference": None,
            "redirect_url": None,
            "error": "Request timeout",
        }
    except Exception as e:
        logger.error(f"Error submitting order: {e}")
        return {
            "order_tracking_id": None,
            "merchant_reference": None,
            "redirect_url": None,
            "error": str(e),
        }


def get_transaction_status(order_tracking_id, access_token):
    """Get transaction status from Pesapal."""
    try:
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
        }

        params = {"orderTrackingId": order_tracking_id}

        response = requests.get(
            TRANSACTION_STATUS_ENDPOINT,
            params=params,
            headers=headers,
            timeout=30,
        )

        if response.status_code == 200:
            result = response.json()
            return {
                "payment_status_description": result.get(
                    "payment_status_description"
                ),
                "confirmation_code": result.get("confirmation_code"),
                "payment_method": result.get("payment_method"),
                "amount": result.get("amount"),
                "currency": result.get("currency"),
                "created_date": result.get("created_date"),
                "error": None,
            }
        else:
            logger.error(
                f"Failed to get transaction status: {response.status_code} - {response.text}"
            )
            return {
                "payment_status_description": None,
                "confirmation_code": None,
                "payment_method": None,
                "amount": None,
                "currency": None,
                "created_date": None,
                "error": f"HTTP {response.status_code}",
            }

    except requests.exceptions.Timeout:
        logger.error("Timeout while getting transaction status")
        return {
            "payment_status_description": None,
            "confirmation_code": None,
            "payment_method": None,
            "amount": None,
            "currency": None,
            "created_date": None,
            "error": "Request timeout",
        }
    except Exception as e:
        logger.error(f"Error getting transaction status: {e}")
        return {
            "payment_status_description": None,
            "confirmation_code": None,
            "payment_method": None,
            "amount": None,
            "currency": None,
            "created_date": None,
            "error": str(e),
        }
