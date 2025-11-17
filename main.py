import os
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

from database import db, create_document, get_documents
from schemas import Project, ContactMessage

app = FastAPI(title="Portfolio Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Portfolio Backend Running"}

@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response

# Seed helper
SEED_PROJECTS: List[Project] = [
    Project(
        title="Microservices Order System",
        description="Event-driven microservices with Spring Boot, Kafka, and Docker for resilient order processing.",
        tech_stack=["Java", "Spring Boot", "Kafka", "Docker", "MongoDB"],
        repo_url="https://github.com/example/order-system",
        live_url=None,
        image_url="https://images.unsplash.com/photo-1518779578993-ec3579fee39f?w=1200&auto=format&fit=crop&q=60",
        featured=True,
    ),
    Project(
        title="Reactive Billing API",
        description="High-throughput reactive REST API using Spring WebFlux and R2DBC.",
        tech_stack=["Java", "Spring WebFlux", "PostgreSQL", "R2DBC", "JWT"],
        repo_url="https://github.com/example/billing-api",
        live_url=None,
        image_url="https://images.unsplash.com/photo-1515879218367-8466d910aaa4?w=1200&auto=format&fit=crop&q=60",
        featured=True,
    ),
    Project(
        title="CI/CD Pipeline as Code",
        description="GitHub Actions pipeline with quality gates, containers, and blue/green deployment.",
        tech_stack=["Java", "Maven", "GitHub Actions", "Docker", "Kubernetes"],
        repo_url="https://github.com/example/cicd-pipeline",
        live_url=None,
        image_url="https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=1200&auto=format&fit=crop&q=60",
        featured=False,
    ),
]

@app.get("/api/projects")
def list_projects():
    """Return portfolio projects from database; seed if empty."""
    try:
        docs = get_documents("project")
        if not docs:
            for p in SEED_PROJECTS:
                create_document("project", p)
            docs = get_documents("project")
        # Normalize ObjectId to string if present
        for d in docs:
            if "_id" in d:
                d["id"] = str(d.pop("_id"))
        return {"projects": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ContactResponse(BaseModel):
    status: str

@app.post("/api/contact", response_model=ContactResponse)
def submit_contact(msg: ContactMessage):
    try:
        payload = msg.model_dump()
        payload["created_at"] = datetime.now(timezone.utc)
        create_document("contactmessage", payload)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
