from fastapi import FastAPI
from pydantic import BaseModel
import json
from pathlib import Path

app = FastAPI()

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
def receive_inquiry(inquiry: Inquiry):
    file_path = Path("inquiries.json")

    if file_path.exists():
        with open(file_path, "r") as file:
            inquiries = json.load(file)
    else:
        inquiries = []

    new_inquiry = inquiry.model_dump()
    new_inquiry["id"] = len(inquiries) + 1

    inquiries.append(new_inquiry)

    with open(file_path, "w") as file:
        json.dump(inquiries, file, indent=4)

    return {
        "status": "success",
        "message": "Inquiry saved successfully",
        "data": inquiry
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
        





