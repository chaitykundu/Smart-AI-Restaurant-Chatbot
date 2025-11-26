import uuid
import qrcode
import base64
from io import BytesIO


# Temporary in-memory store (replace with database later)
# Structure:
# {
#    "token": {
#        "offer": "10% OFF at Ramen Manila",
#        "is_used": False
#    }
# }
qr_store = {}


def generate_unique_qr(offer_text: str):
    """
    Generates a unique, one-time-use QR code.
    Returns the token and the base64 QR image.
    """

    # 1. Create unique token
    token = str(uuid.uuid4())

    # 2. Save token in local store
    qr_store[token] = {
        "offer": offer_text,
        "is_used": False
    }

    # 3. Prepare QR content (validation URL)
    qr_data = f"https://your-domain.com/validate_qr?token={token}"

    # 4. Generate QR code
    qr_img = qrcode.make(qr_data)

    # 5. Convert to base64
    buffer = BytesIO()
    qr_img.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return {
        "token": token,
        "qr_code": qr_base64
    }


def validate_qr_token(token: str):
    """
    Validates a QR token.
    Returns status and offer details.
    """

    # Token not found
    if token not in qr_store:
        return {
            "status": "invalid",
            "message": "QR token not found."
        }

    data = qr_store[token]

    # Already used
    if data["is_used"]:
        return {
            "status": "expired",
            "message": "This QR code has already been used."
        }

    # Mark as used
    data["is_used"] = True

    return {
        "status": "success",
        "message": "QR is valid. Offer applied!",
        "offer": data["offer"]
    }
