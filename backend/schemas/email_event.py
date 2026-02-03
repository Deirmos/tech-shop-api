from pydantic import BaseModel, EmailStr


class EmailOrderConfirmationEvent(BaseModel):
    email_to: EmailStr
    template_data: dict
