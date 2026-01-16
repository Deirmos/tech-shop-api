import aiosmtplib
import os
from email.message import EmailMessage
from jinja2 import Environment, FileSystemLoader
from pathlib import Path

from backend.core.config import settings

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_FOLDER = BASE_DIR / "templates" / "email"
env = Environment(loader=FileSystemLoader(TEMPLATE_FOLDER))



class EmailService:

    @staticmethod
    async def send_order_confirmation(
        email_to: str,
        template_data: dict
    ):
        
        template = env.get_template("order_confirmation.html")
        html_content = template.render(**template_data)

        message = EmailMessage()
        message["From"] = settings.MAIL_FROM
        message["To"] = email_to
        message["Subject"] = f"Заказ №{template_data['order_id']} - TechShop"

        message.add_alternative(html_content, subtype="html")


        await aiosmtplib.send(
            message,
            hostname=settings.MAIL_SERVER,
            port=settings.MAIL_PORT,
            username=settings.MAIL_USERNAME,
            password=settings.MAIL_PASSWORD,
            use_tls=(settings.MAIL_PORT == 465),
            start_tls=(settings.MAIL_PORT == 587 or settings.MAIL_PORT == 2525)
        )

email_service = EmailService()