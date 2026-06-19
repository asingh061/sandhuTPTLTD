from fastapi import FastAPI
from pydantic import BaseModel
import json
from pathlib import Path
from sqlalchemy.orm import Session
from database import SessionLocal
from models import InquiryDB
from schemas import InquiryCreate
from schemas import InquiryCreate, AIQuestion
import os
from dotenv import load_dotenv
from openai import OpenAI
from fastapi.middleware.cors import CORSMiddleware
from rag import find_best_context

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        pass

@app.get("/")
def home():
    return {
        "message": "Sandhu Transport Backend is working"
    }

@app.get("/api/company")
def get_company():
    return {
        "name": "Sandhu Transport Limited",
        "location": "Zambia",
        "service": "Transport and Logistics"
    }

class Inquiry(BaseModel):
    name: str
    email: str
    phone: str
    message: str

@app.post("/api/inquiry")

def receive_inquiry(inquiry: InquiryCreate):
    db = get_db()

    new_inquiry = InquiryDB(
        name=inquiry.name,
        email=inquiry.email,
        phone=inquiry.phone,
        message=inquiry.message
    )

    db.add(new_inquiry)
    db.commit()
    db.refresh(new_inquiry)
    db.close()

    return {
        "status": "success",
        "message": "Inquiry saved to database",
        "data": new_inquiry
    }

@app.get("/api/inquiries")
def get_inquires():
    file_path = Path("inquiries.json")

    if not file_path.exists():
        return[]
    
    with open(file_path,"r") as file:
        return json.load(file)
    
@app.get("/api/inquiries/{id}")
def get_inquiry(id: int):
    file_path = Path("inquiries.json")

    if not file_path.exists():
        return {"error" :"no inguiries found"}
    
    with open(file_path,"r") as file:
        inquiries = json.load(file)

    for inquiry in inquiries:
        if inquiry["id"] == id:
            return inquiry
    
    return {"error":"inquiry not found"}

@app.get("/api/search")
def search_inquiries(name: str):
    file_path = Path("inquiries.json")

    if not file_path.exists():
        return []

    with open(file_path,"r") as file:
        inquiries = json.load(file)

    results = []

    for inquiry in inquiries:
        if inquiry["name"].lower() == name.lower():
            results.append(inquiry)

    return results

@app.get("/api/db-inquiries")
def get_db_inquiries():
    db = get_db()

    inquiries = db.query(InquiryDB).all()

    db.close()

    return inquiries

def load_company_info():
    with open("company_info.txt", "r", encoding="utf-8") as file:
        return file.read()
        
@app.post("/api/ask-ai")
def ask_ai(request: AIQuestion):
    context = find_best_context(request.question)

    response = client.responses.create(
        model="gpt-4.1-mini",
        instructions=f"""
You are Sandhu AI, the official assistant for Sandhu Transport Zambia.

Answer the user's question using only this retrieved company information:

{context}

Keep answers short, professional, and direct.

If the user asks something unrelated, say:
"I can only answer questions related to Sandhu Transport and the information available on our website."

If the answer is not in the retrieved information, say:
"I couldn't find that information on the Sandhu Transport website. Please contact our team directly for assistance."
""",
        input=request.question
    )

    return {
        "question": request.question,
        "context_used": context,
        "answer": response.output_text
    }

