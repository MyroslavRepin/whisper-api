from typing import Dict
import resend
import base64
from loguru import logger

def send_mail(transcription_text: str) -> Dict:
    params: resend.Emails.SendParams = {
        "from": "Acme <whisper-api@myroslavrepin.com>",
        "to": ["myroslavrepin@gmail.com"],
        "subject": "Transcription finished",
        "attachments": [
            {
                "filename": "transcript.txt",
                "content": base64.b64encode(transcription_text.encode("utf-8")).decode("utf-8"),
            }
        ],
        "text": "Transcription in an attachment"
    }
    try:
        logger.info("Sending transcription email to myroslavrepin@gmail.com")
        email: resend.Emails.SendResponse = resend.Emails.send(params)
        logger.info(f"Email sent successfully: {email}")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        raise e
    return email
