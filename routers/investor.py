from fastapi import APIRouter, HTTPException, Header, Query
from models import LandResponse, InvestmentCreate, InvestmentResponse, LandBase, WalletTransaction
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

# 19. POST /invest/wallet/add
@router.post("/wallet/add")
def add_funds(transaction: WalletTransaction, user_id: str = Header(..., alias="X-User-ID")):
    # 1. Get current balance
    user_res = supabase.table("users").select("Balance").eq("id", user_id).execute()
    if not user_res.data:
        raise HTTPException(status_code=404, detail="User not found")
    
    current_balance = user_res.data[0]['Balance'] or 0.0
    new_balance = int(current_balance + transaction.amount)
    
    # 2. Update balance
    supabase.table("users").update({"Balance": new_balance}).eq("id", user_id).execute()
    return {"message": "Funds added successfully", "balance": new_balance}

# 20. POST /invest/wallet/withdraw
@router.post("/wallet/withdraw")
def withdraw_funds(transaction: WalletTransaction, user_id: str = Header(..., alias="X-User-ID")):
    # 1. Get current balance
    user_res = supabase.table("users").select("Balance").eq("id", user_id).execute()
    if not user_res.data:
        raise HTTPException(status_code=404, detail="User not found")
        
    current_balance = user_res.data[0]['Balance'] or 0.0
    
    if current_balance < transaction.amount:
         raise HTTPException(status_code=400, detail="Insufficient funds")

    new_balance = int(current_balance - transaction.amount)
    
    # 2. Update balance
    supabase.table("users").update({"Balance": new_balance}).eq("id", user_id).execute()
    return {"message": "Funds withdrawn successfully", "balance": new_balance}


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

    # 2. Check User Balance (Optional but recommended)
    # user = supabase.table("users").select("Balance").eq("id", investment.investor_id).execute()
    # if not user.data or user.data[0]['Balance'] < investment.amount:
    #     raise HTTPException(status_code=400, detail="Insufficient Wallet Balance")

    # 3. Reserve (Update Land Status)
    # This removes it from the 'available' marketplace view
    supabase.table("lands").update({"status": "reserved"}).eq("id", investment.land_id).execute()

    # 4. Create Investment Record
    data = {
        "land_id": investment.land_id,
        "investor_id": investment.investor_id,
        "amount": investment.amount,
        "status": "pending_approval" # Admin approval needed to go Active
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
    # Return ALL investments (pending, active, etc.) so user can see status
    response = supabase.table("investments").select("*").eq("investor_id", user_id).execute()
    return response.data

# 17. GET /invest/notifications
@router.get("/notifications")
def get_notifications(user_id: str = Header(..., alias="X-User-ID")):
    # Mock notifications
    return [
        {"id": 1, "message": "Welcome to the platform!"},
        {"id": 2, "message": "Check available lands now."}
    ]
