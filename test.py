from fastapi import FastAPI, UploadFile, File, Form
from typing import Optional

app = FastAPI(title="Upload Test API")


@app.post("/test-chat")
async def test_chat(
    session_id: str = Form(...),
    message: str = Form(""),
    file: Optional[UploadFile] = File(None)
):
    return {
        "session_id": session_id,
        "message": message,
        "filename": file.filename if file else None,
        "content_type": file.content_type if file else None,
    }
