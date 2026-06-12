import base64
import email
from collections.abc import Sequence

import resend
from loguru import logger


class EmailService:
    DEFAULT_FROM = "Acme <whisper-api@myroslavrepin.com>"
    DEFAULT_TO = ["myroslavrepin@gmail.com"]

    def __init__(self, api_key: str):
        self.api_key = api_key
        resend.api_key = self.api_key

    def send_email(
        self,
        to: list[str] | str,
        subject: str,
        text: str,
        from_email: str | None = None,
        html: str | None = None,
        attachments: Sequence[resend.Attachment | resend.RemoteAttachment]
        | None = None,
    ):
        """Send email with text body. Simplified generic method."""
        if isinstance(to, str):
            to = [to]

        params: resend.Emails.SendParams = {
            "from": from_email or self.DEFAULT_FROM,
            "to": to,
            "subject": subject,
            "text": text,
        }

        return resend.Emails.send(params)

    def send_with_attachment(
        self,
        to: list[str] | str,
        subject: str,
        body: str,
        filename: str,
        content: str,
        from_email: str | None = None,
    ):
        """Send email with text file attachment."""
        if isinstance(to, str):
            to = [to]

        attachments: list[resend.Attachment] = [
            {
                "filename": filename,
                "content": base64.b64encode(content.encode("utf-8")).decode("utf-8"),
            }
        ]

        return self.send_email(
            to=to,
            subject=subject,
            text=body,
            from_email=from_email,
            attachments=attachments,
        )

    def send_mail(self, text):
        """Legacy method - sends transcription as attachment."""
        return self.send_with_attachment(
            to=self.DEFAULT_TO,
            subject="Transcription finished",
            body="Transcription in an attachment",
            filename="transcript.txt",
            content=text,
        )
