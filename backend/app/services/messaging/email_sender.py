import smtplib
import ssl
from email.mime.text import MIMEText

from app.core.config import get_settings

UNSUBSCRIBE_FOOTER = (
    "\n\n---\n"
    "If you'd rather not receive messages like this, just reply \"UNSUBSCRIBE\" "
    "and you won't be contacted again."
)


class EmailNotConfiguredError(RuntimeError):
    pass


def send_email(to_address: str, subject: str, body: str) -> None:
    settings = get_settings()
    if not settings.gmail_address or not settings.gmail_app_password:
        raise EmailNotConfiguredError(
            "GMAIL_ADDRESS / GMAIL_APP_PASSWORD are not set in backend/.env"
        )

    message = MIMEText(body + UNSUBSCRIBE_FOOTER, "plain")
    message["Subject"] = subject
    message["From"] = settings.gmail_address
    message["To"] = to_address

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port, context=context) as server:
        server.login(settings.gmail_address, settings.gmail_app_password)
        server.sendmail(settings.gmail_address, [to_address], message.as_string())
