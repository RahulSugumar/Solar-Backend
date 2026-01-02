from fastapi import APIRouter, HTTPException, Header, Query
from models import LandResponse, InvestmentCreate, InvestmentResponse, LandBase
from database import supabase
from typing import List, Optional

router = APIRouter(prefix="/invest", tags=["Investor"])

# 18. GET /invest/wallet
@router.get("/wallet")
def get_wallet_balance(user_id: str = Header(..., alias="X-User-ID")):
    # Fetch user balance
    response = supabase.table("users").select("balance").eq("id", user_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="User wallet not found")
    return {"balance": response.data[0]['balance']}

# 12. GET /invest/available-lands?location=
@router.get("/available-lands", response_model=List[LandResponse])
def search_lands(location: Optional[str] = Query(None)):
    query = supabase.table("lands").select("*").eq("status", "available")
    if location:
        # Simple text match (ilike if supported via library or just exact match for MVP)
        # supabase-py might allow .ilike('location', f'%{location}%')
        query = query.ilike("location", f"%{location}%")
    
    response = query.execute()
    return response.data

# 13. GET /invest/land/:id
@router.get("/land/{land_id}", response_model=LandResponse)
def get_land_details(land_id: str):
    response = supabase.table("lands").select("*").eq("id", land_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Land not found")
    return response.data[0]

# 14. POST /invest/request (Reserve Land)
@router.post("/request", response_model=InvestmentResponse)
def request_land(investment: InvestmentCreate):
    # 1. Check Availability
    land = supabase.table("lands").select("status").eq("id", investment.land_id).execute()
    if not land.data or land.data[0]['status'] != 'available':
        raise HTTPException(status_code=400, detail="Land not available")

    # 2. Reserve (Update Land)
    supabase.table("lands").update({"status": "reserved"}).eq("id", investment.land_id).execute()

    # 3. Create Investment Record
    data = {
        "land_id": investment.land_id,
        "investor_id": investment.investor_id,
        "amount": investment.amount,
        "status": "pending_payment" # waiting for admin manual confirm
    }
    response = supabase.table("investments").insert(data).execute()
    return response.data[0]

# 15. GET /invest/my-requests
@router.get("/my-requests", response_model=List[InvestmentResponse])
def get_my_requests(user_id: str = Header(..., alias="X-User-ID")):
    # Pending investments
    response = supabase.table("investments").select("*").eq("investor_id", user_id).neq("status", "completed").execute()
    return response.data

# 16. GET /invest/my-investments
@router.get("/my-investments", response_model=List[InvestmentResponse])
def get_my_investments(user_id: str = Header(..., alias="X-User-ID")):
    # Active/Completed investments
    response = supabase.table("investments").select("*").eq("investor_id", user_id).eq("status", "completed").execute()
    return response.data

# 17. GET /invest/notifications
@router.get("/notifications")
def get_notifications(user_id: str = Header(..., alias="X-User-ID")):
    # Mock notifications
    return [
        {"id": 1, "message": "Welcome to the platform!"},
        {"id": 2, "message": "Check available lands now."}
    ]
