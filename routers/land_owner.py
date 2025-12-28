from fastapi import APIRouter, HTTPException, Header
from models import LandCreate, LandResponse
from database import supabase
from typing import List

router = APIRouter(prefix="/land", tags=["Land Owner"])

# 8. POST /land/submit
@router.post("/submit", response_model=LandResponse)
def submit_land(land: LandCreate):
    # Default status could be 'pending_approval' if admin needs to check first
    # For MVP user flow, let's assume it goes to 'available' or 'pending'
    # User asked for Admin Approval flow later (Endpoint 22), so let's default to 'pending_approval'
    # But schema default is 'available'. Let's override.
    
    data = land.dict()
    data['status'] = 'pending_approval' 
    
    try:
        print(f"DEBUG: Submitting Land Data: {data}")
        response = supabase.table("lands").insert(data).execute()
        print(f"DEBUG: Supabase Response: {response}")
    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
        # Check if it has 'details'
        if hasattr(e, 'details'):
             print(f"DETAILS: {e.details}")
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}")

    if not response.data:
        raise HTTPException(status_code=500, detail="Failed to submit land - No Data Returned")
    return response.data[0]

# 9. GET /land/my-lands
@router.get("/my-lands", response_model=List[LandResponse])
def get_my_lands(user_id: str = Header(..., alias="X-User-ID")):
    response = supabase.table("lands").select("*").eq("owner_id", user_id).execute()
    return response.data

# 10. GET /land/my-earnings
@router.get("/my-earnings")
def get_my_earnings(user_id: str = Header(..., alias="X-User-ID")):
    # Mock calculation based on active lands
    lands = supabase.table("lands").select("*").eq("owner_id", user_id).eq("status", "active").execute().data
    
    # Formula: Base rent + Share
    total_earnings = 0
    for l in lands:
        total_earnings += 5000 # Fixed base
    
    return {"total_earnings": total_earnings, "breakdown": "Fixed Rent + 10% Share"}

# 11. GET /land/map
@router.get("/map", response_model=List[LandResponse])
def get_owner_map(user_id: str = Header(..., alias="X-User-ID")):
    # Show user's lands on map (active ones usually)
    response = supabase.table("lands").select("*").eq("owner_id", user_id).execute()
    return response.data
