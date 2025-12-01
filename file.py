from fastapi import UploadFile


# -------------------------------------
# Prepare uploaded file for Gemini Vision
# -------------------------------------
async def prepare_gemini_file(upload: UploadFile):
    """
    Reads an uploaded file (image, PDF, menu photo, etc.)
    and converts it into the format required by Gemini Vision.

    Returns:
        dict | None
        A dictionary containing:
            - mime_type: str
            - data: bytes
        OR None if no file is uploaded.
    """

    # No file provided
    if upload is None:
        return None

    # Read the file bytes
    file_bytes = await upload.read()

    # Support if empty file uploaded
    if not file_bytes:
        return None

    # Return Gemini-compatible structure
    return {
        "mime_type": upload.content_type,
        "data": file_bytes
    }
