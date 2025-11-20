import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Snowboardproduct, Review

app = FastAPI(title="Snowboard Reviews Affiliate API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Snowboard Reviews Affiliate API draait"}


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
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
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

    return response


# Helpers
class ProductQuery(BaseModel):
    zoekterm: Optional[str] = None
    stijl: Optional[str] = None
    merk: Optional[str] = None


def serialize_doc(doc: dict):
    doc["id"] = str(doc.pop("_id"))
    return doc


# Endpoints: Products
@app.post("/api/products", response_model=dict)
def create_product(product: Snowboardproduct):
    try:
        inserted_id = create_document("snowboardproduct", product)
        return {"id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/products", response_model=List[dict])
def list_products(zoekterm: Optional[str] = None, stijl: Optional[str] = None, merk: Optional[str] = None):
    try:
        query = {}
        if zoekterm:
            query["$or"] = [
                {"naam": {"$regex": zoekterm, "$options": "i"}},
                {"beschrijving": {"$regex": zoekterm, "$options": "i"}},
                {"tags": {"$regex": zoekterm, "$options": "i"}},
            ]
        if stijl:
            query["stijl"] = {"$regex": stijl, "$options": "i"}
        if merk:
            query["merk"] = {"$regex": merk, "$options": "i"}

        docs = get_documents("snowboardproduct", query)
        return [serialize_doc(d) for d in docs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/products/{product_id}", response_model=dict)
def get_product(product_id: str):
    try:
        doc = db["snowboardproduct"].find_one({"_id": ObjectId(product_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="Product niet gevonden")
        return serialize_doc(doc)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Endpoints: Reviews
@app.post("/api/reviews", response_model=dict)
def create_review(review: Review):
    try:
        # Validate product_id
        pid = review.product_id
        # Check existence
        prod = db["snowboardproduct"].find_one({"_id": ObjectId(pid)})
        if not prod:
            raise HTTPException(status_code=404, detail="Product niet gevonden")
        inserted_id = create_document("review", review)
        # update average rating
        reviews = list(db["review"].find({"product_id": pid}))
        if reviews:
            avg = sum([r.get("rating", 0) for r in reviews]) / len(reviews)
            db["snowboardproduct"].update_one({"_id": ObjectId(pid)}, {"$set": {"gemiddelde_rating": round(avg, 2)}})
        return {"id": inserted_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/products/{product_id}/reviews", response_model=List[dict])
def list_reviews(product_id: str):
    try:
        docs = get_documents("review", {"product_id": product_id})
        return [serialize_doc(d) for d in docs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
