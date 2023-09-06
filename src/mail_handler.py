import os
import smtplib
from email.message import EmailMessage
from typing import List

from dotenv import load_dotenv

from helper_functions import prettify_list_of_flats

load_dotenv()


def sent_flat_info_list(flats: List[dict], receiver_mail_address: str) -> dict:
    mail_text = prettify_list_of_flats(flats)
    if mail_text:
        port = int(os.getenv("SMTP_PORT"))
        host = os.getenv("SMTP_HOST")
        user = os.getenv("SMTP_USER")
        password = os.getenv("SMTP_PW")
        from_addr = os.getenv("SMTP_FROM")

        mailserver = smtplib.SMTP(host=host, port=port)
        mailserver.starttls()
        mailserver.login(user=user, password=password)

        msg = EmailMessage()
        msg["Subject"] = "neue tolle wohnungen"
        msg["From"] = from_addr
        msg["To"] = receiver_mail_address
        msg.set_content(mail_text)

        send_errors = mailserver.send_message(msg)

        mailserver.quit()
        return send_errors
