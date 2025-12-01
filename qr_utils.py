import qrcode
import uuid
import base64
from io import BytesIO
import os

# QR folder (optional, not required for base64 return)
QR_FOLDER = "qr_codes"
os.makedirs(QR_FOLDER, exist_ok=True)

# Temporary in-memory store for tracking promo codes
promo_store = {}
# Structure:
# {
#     "token123": {
#         "offer": "...",
#         "used": False
#     }
# }


def generate_unique_qr(offer_text: str):
    """
    Generate a one-time QR for the given offer.
    Returns:
        {
          "token": str,
          "qr_code": base64_image_string
        }
    """

    # Create unique token
    token = str(uuid.uuid4())

    # Save record in store
    promo_store[token] = {
        "offer": offer_text,
        "used": False
    }

    # QR content (your future redeem endpoint)
    qr_url = f"https://yourapp.com/promo/redeem?token={token}"

    # Generate QR image
    qr_img = qrcode.make(qr_url)

    # Convert to base64
    buffer = BytesIO()
    qr_img.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    return {
        "token": token,
        "qr_code": qr_base64
    }
