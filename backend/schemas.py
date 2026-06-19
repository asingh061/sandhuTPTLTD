from pydantic import BaseModel


class InquiryCreate(BaseModel):
    name: str
    email: str
    phone: str
    message: str