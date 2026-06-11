import base64

import resend
from loguru import logger


class EmailService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        resend.api_key = self.api_key

    def send_email(self, to: str, subject: str, text: str, from_email: str | None = None):
        """Send simple text email."""
        params: resend.Emails.SendParams = {
            "from": from_email or "Acme <whisper-api@myroslavrepin.com>",
            "to": [to],
            "subject": subject,
            "text": text,
        }

        try:
            logger.info(f"Sending email to {to} - subject: {subject}")
            email: resend.Emails.SendResponse = resend.Emails.send(params)
            logger.info(f"Email sent successfully: {email}")
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            raise e
        return email

    def send_mail(self, text):
        """Send transcription as attachment."""
        params: resend.Emails.SendParams = {
            "from": "Acme <whisper-api@myroslavrepin.com>",
            "to": ["myroslavrepin@gmail.com"],
            "subject": "Transcription finished",
            "attachments": [
                {
                    "filename": "transcript.txt",
                    "content": base64.b64encode(text.encode("utf-8")).decode("utf-8"),
                }
            ],
            "text": "Transcription in an attachment",
        }
        try:
            logger.info("Sending transcription email to myroslavrepin@gmail.com")
            email: resend.Emails.SendResponse = resend.Emails.send(params)
            logger.info(f"Email sent successfully: {email}")
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            raise e
        return email
