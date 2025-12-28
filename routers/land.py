from fastapi import APIRouter, HTTPException
from models import LandCreate, LandResponse
from database import supabase
from typing import List, Optional

router = APIRouter(prefix="/lands", tags=["Lands"])

@router.get("/", response_model=List[LandResponse])
def get_lands(status: Optional[str] = None):
    query = supabase.table("lands").select("*")
    if status:
        query = query.eq("status", status)
    
    response = query.execute()
    return response.data

@router.post("/", response_model=LandResponse)
def create_land(land: LandCreate):
    # Verify owner exists
    owner = supabase.table("users").select("id").eq("id", land.owner_id).execute()
    if not owner.data:
        raise HTTPException(status_code=404, detail="Owner not found")

    data = land.dict()
    response = supabase.table("lands").insert(data).execute()
    
    if not response.data:
        raise HTTPException(status_code=500, detail="Failed to create land")
        
    return response.data[0]

@router.get("/{land_id}", response_model=LandResponse)
def get_land(land_id: str):
    response = supabase.table("lands").select("*").eq("id", land_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Land not found")
    return response.data[0]
