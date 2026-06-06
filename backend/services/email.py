from typing import Dict
import resend
import base64

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
        email: resend.Emails.SendResponse = resend.Emails.send(params)
    except Exception as e:
        raise e
    return email
