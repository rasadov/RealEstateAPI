"""Module contains utility functions for the base src."""

import smtplib
from email.mime.text import MIMEText

from src.config import Settings

def send_email(email: str, subject: str, body: str, sender: str = None) -> None:
    """
    Sends an email to the specified email address.
    """
    message = MIMEText(body)
    message["Subject"] = subject
    message["From"] = sender or Settings.EMAIL_SENDER
    message["To"] = email

    with smtplib.SMTP_SSL(Settings.SMTP_SERVER, Settings.SMTP_PORT) as server:
        server.login(Settings.SMTP_USER, Settings.SMTP_PASSWORD)
        server.sendmail(Settings.EMAIL_SENDER, [email], message.as_string())

def send_email_verification(email: str, token: str) -> None:
    """
    Send an email verification email to the specified email address.
    """
    subject = "Verify your email address"
    body = f"Click the link to verify your email address: {Settings.FRONTEND_URL}/verify-email?token={token}"
    send_email(email, subject, body)

def send_password_reset(email: str, token: str) -> None:
    """
    Send a password reset email to the specified email address.
    """
    subject = "Reset your password"
    body = f"Click the link to reset your password: {Settings.FRONTEND_URL}/reset-password?token={token}"
    send_email(email, subject, body)
