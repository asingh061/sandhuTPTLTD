from sqlalchemy import Column, Integer, String
from database import Base


class InquiryDB(Base):
    __tablename__ = "inquiries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String)
    phone = Column(String)
    message = Column(String)