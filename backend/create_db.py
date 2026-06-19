from database import engine, Base
from models import InquiryDB

Base.metadata.create_all(bind=engine)

print("Database created successfully!")