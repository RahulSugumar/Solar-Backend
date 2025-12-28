from fastapi import APIRouter, HTTPException, Header
from models import LandResponse, InvestmentResponse
from database import supabase
from typing import List

router = APIRouter(prefix="/admin", tags=["Admin"])

# 19. GET /admin/investor-requests
@router.get("/investor-requests", response_model=List[InvestmentResponse])
def get_investor_requests():
    # Investments pending payment
    response = supabase.table("investments").select("*").eq("status", "pending_payment").execute()
    return response.data

# 20. GET /admin/land-requests
@router.get("/land-requests", response_model=List[LandResponse])
def get_land_requests():
    # Lands pending approval
    response = supabase.table("lands").select("*").eq("status", "pending_approval").execute()
    return response.data

# 21. POST /admin/investor-approve
@router.post("/investor-approve")
def approve_investor_request(investment_id: str, final_amount: float = None):
    # Admin calls investor, agrees on amount, then approves.
    update_data = {"status": "approved_waiting_payment"}
    if final_amount:
        update_data["amount"] = final_amount
        
    response = supabase.table("investments").update(update_data).eq("id", investment_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Request not found")
    return {"message": "Investor request approved, waiting for payment"}

# 22. POST /admin/land-approve
@router.post("/land-approve")
def approve_land(land_id: str):
    response = supabase.table("lands").update({"status": "available"}).eq("id", land_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Land not found")
    return {"message": "Land approved and is now Available"}
