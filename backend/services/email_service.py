from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pathlib import Path

from backend.core.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=True
)

class EmailService:

    @staticmethod
    async def send_order_confirmation(
        email_to: str,
        order_id: int,
        total_price: float
    ):
        html = f"""
        <html>
            <body>
                <h1>Заказ №{order_id} успешно оформлен!</h1>
                <p>Спасибо за покупку в нашем магазине.</p>
                <p><b>Сумма заказа:</b> {total_price} руб.</p>
                <p>Мы свяжемся с вами в ближайшее время для уточнения деталей доставки.</p>
            </body>
        </html>   
        """

        message = MessageSchema(
            subject="Подтверждение заказа - TechShop",
            recipients=[email_to],
            body=html,
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message)

email_service = EmailService()