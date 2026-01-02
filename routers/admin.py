from fastapi import APIRouter, HTTPException, Header, Depends
from typing import List, Optional
from database import supabase
from pydantic import BaseModel

router = APIRouter(prefix="/admin", tags=["Admin"])

# --- Models ---
class AdminStatResponse(BaseModel):
    total_users: int
    active_lands: int
    pending_lands: int
    pending_investments: int
    total_volume: float

class AdminAction(BaseModel):
    action: str # 'approve', 'reject'
    notes: Optional[str] = None

# --- Helpers ---
def verify_admin(user_id: str):
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    res = supabase.table('users').select("role").eq("id", user_id).execute()
    if not res.data or res.data[0]['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Admin Access Only")
    return True

# --- Endpoints ---

@router.get("/stats", response_model=AdminStatResponse)
def get_admin_stats(user_id: str = Header(None, alias="X-User-ID")):
    verify_admin(user_id)
    
    # 1. Users
    users = supabase.table("users").select("id", count='exact').execute()
    
    # 2. Lands
    active_lands = supabase.table("lands").select("id", count='exact').eq("status", "active").execute()
    pending_lands = supabase.table("lands").select("id", count='exact').eq("status", "pending_approval").execute() # pending verification
    
    # 3. Investments (Volume)
    investments = supabase.table("investments").select("*").execute()
    total_vol = sum(i['amount'] for i in investments.data if i['status'] in ['active', 'completed'])
    pending_inv = len([i for i in investments.data if i['status'] == 'pending_approval'])

    return {
        "total_users": users.count or 0,
        "active_lands": active_lands.count or 0,
        "pending_lands": pending_lands.count or 0,
        "pending_investments": pending_inv,
        "total_volume": total_vol
    }

# --- Land Management ---

@router.get("/lands/pending")
def get_pending_lands(user_id: str = Header(None, alias="X-User-ID")):
    verify_admin(user_id)
    # Fetch lands that need approval
    res = supabase.table("lands").select("*, users(full_name, email)").eq("status", "pending_approval").execute()
    return res.data

@router.post("/lands/{land_id}/approve")
def approve_land(land_id: str, user_id: str = Header(None, alias="X-User-ID")):
    verify_admin(user_id)
    
    # Update Status to 'open' (Available for investors)
    res = supabase.table("lands").update({"status": "available"}).eq("id", land_id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Land not found")
    return {"message": "Land Approved and is now Open for Investment"}

@router.post("/lands/{land_id}/reject")
def reject_land(land_id: str, user_id: str = Header(None, alias="X-User-ID")):
    verify_admin(user_id)
    res = supabase.table("lands").update({"status": "rejected"}).eq("id", land_id).execute()
    return {"message": "Land Rejected"}

# --- Investment Management ---

@router.get("/investments/pending")
def get_pending_investments(user_id: str = Header(None, alias="X-User-ID")):
    verify_admin(user_id)
    # Fetch investments waiting for approval (status: pending_approval)
    res = supabase.table("investments").select("*, lands(location, area_sqft), users(full_name, email)").eq("status", "pending_approval").execute()
    return res.data

@router.post("/investments/{inv_id}/approve")
def approve_investment(inv_id: str, user_id: str = Header(None, alias="X-User-ID")):
    verify_admin(user_id)
    
    # 1. Update Investment Status -> 'payment_pending'
    # This unlocks the "Pay Now" button for the investor
    res = supabase.table("investments").update({"status": "payment_pending"}).eq("id", inv_id).execute()
    
    if not res.data:
         raise HTTPException(status_code=404, detail="Investment not found")
         
    return {"message": "Investment Approved. Status set to Payment Due."}
