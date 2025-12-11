from fastapi import UploadFile

# -------------------------------------
# Prepare uploaded file for OpenAI Vision
# -------------------------------------
async def prepare_uploaded_file(upload: UploadFile):
    """
    Reads an uploaded file (image, PDF, menu photo, etc.)
    and returns its raw bytes and mime type.

    Returns:
        dict | None:
            {
                "mime_type": str,
                "data": bytes
            }
        OR None if no file is provided.
    """

    # No file provided
    if upload is None:
        return None

    # Read uploaded file data
    file_bytes = await upload.read()

    # If file is empty or unreadable
    if not file_bytes:
        return None

    # Return standard file structure for OpenAI Vision models
    return {
        "mime_type": upload.content_type,
        "data": file_bytes
    }
