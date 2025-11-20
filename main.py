import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Timetable, Resource, Doubt

app = FastAPI(title="Timetable & Resources API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helpers
class IDModel(BaseModel):
    id: str


def ensure_object_id(id_str: str) -> ObjectId:
    try:
        return ObjectId(id_str)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid id")


@app.get("/")
def read_root():
    return {"message": "Timetable & Resources Backend Running"}


@app.get("/test")
def test_database():
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
            response["database"] = "✅ Connected & Working"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name
            response["connection_status"] = "Connected"
            try:
                response["collections"] = db.list_collection_names()
            except Exception as e:
                response["database"] = f"⚠️ Connected but error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"
    return response


# Timetable Endpoints
@app.post("/api/timetable", response_model=dict)
def create_timetable(entry: Timetable):
    inserted_id = create_document("timetable", entry)
    return {"id": inserted_id}


@app.get("/api/timetable", response_model=List[dict])
def list_timetable(day: Optional[str] = None):
    filt = {"day": day} if day else {}
    docs = get_documents("timetable", filt)
    # Convert ObjectId to string
    for d in docs:
        d["id"] = str(d.pop("_id"))
    return docs


@app.delete("/api/timetable/{item_id}")
def delete_timetable(item_id: str):
    oid = ensure_object_id(item_id)
    res = db["timetable"].delete_one({"_id": oid})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return {"ok": True}


# Resources Endpoints
@app.post("/api/resources", response_model=dict)
def create_resource(resource: Resource):
    inserted_id = create_document("resource", resource)
    return {"id": inserted_id}


@app.get("/api/resources", response_model=List[dict])
def list_resources(topic: Optional[str] = None):
    filt = {"topic": topic} if topic else {}
    docs = get_documents("resource", filt)
    for d in docs:
        d["id"] = str(d.pop("_id"))
    return docs


@app.delete("/api/resources/{res_id}")
def delete_resource(res_id: str):
    oid = ensure_object_id(res_id)
    res = db["resource"].delete_one({"_id": oid})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return {"ok": True}


# Doubts (Q&A) Endpoints
@app.post("/api/doubts", response_model=dict)
def create_doubt(doubt: Doubt):
    inserted_id = create_document("doubt", doubt)
    return {"id": inserted_id}


@app.get("/api/doubts", response_model=List[dict])
def list_doubts(status: Optional[str] = None):
    filt = {"status": status} if status else {}
    docs = get_documents("doubt", filt)
    for d in docs:
        d["id"] = str(d.pop("_id"))
    return docs


class AnswerPayload(BaseModel):
    answer: str
    answered_by: Optional[str] = None


@app.patch("/api/doubts/{doubt_id}")
def answer_doubt(doubt_id: str, payload: AnswerPayload):
    oid = ensure_object_id(doubt_id)
    update = {"$set": {"answer": payload.answer, "answered_by": payload.answered_by, "status": "answered"}}
    res = db["doubt"].update_one({"_id": oid}, update)
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return {"ok": True}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
