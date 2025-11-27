# qr_utils.py
import qrcode
import uuid
import os

# Ensure the folder exists
QR_FOLDER = "qr_codes"
os.makedirs(QR_FOLDER, exist_ok=True)

def generate_qr_for_promo(promo_text: str):
    """
    Generate a unique QR code for a promo.
    
    Returns:
        promo_code (str): short unique promo code
        file_path (str): path to saved QR image
    """
    # Generate short unique code
    promo_code = str(uuid.uuid4())[:8]

    # Create promo URL for QR
    promo_url = f"https://yourapp.com/promo/redeem?code={promo_code}&promo={promo_text}"

    # Generate QR image
    img = qrcode.make(promo_url)
    file_path = os.path.join(QR_FOLDER, f"{promo_code}.png")
    img.save(file_path)

    return promo_code, file_path
