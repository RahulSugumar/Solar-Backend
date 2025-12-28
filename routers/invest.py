from fastapi import APIRouter, HTTPException
from models import InvestmentCreate, InvestmentResponse
from database import supabase
from datetime import datetime

router = APIRouter(prefix="/invest", tags=["Investments"])

@router.post("/reserve", response_model=InvestmentResponse)
def reserve_land(investment: InvestmentCreate):
    # 1. Check if Land is Available
    land = supabase.table("lands").select("status, total_price").eq("id", investment.land_id).execute()
    if not land.data:
        raise HTTPException(status_code=404, detail="Land not found")
    
    land_info = land.data[0]
    if land_info["status"] != "available":
        raise HTTPException(status_code=400, detail="Land is not available for reservation")

    # 2. Check Amount (optional validation)
    if investment.amount < land_info["total_price"]:
        raise HTTPException(status_code=400, detail="Investment amount must cover total price")

    # 3. Create Investment Record (Pending)
    invest_data = {
        "land_id": investment.land_id,
        "investor_id": investment.investor_id,
        "amount": investment.amount,
        "status": "pending"
    }
    inv_res = supabase.table("investments").insert(invest_data).execute()
    if not inv_res.data:
        raise HTTPException(status_code=500, detail="Failed to create investment record")

    # 4. Update Land Status to 'reserved' (Atomic-ish)
    # Note: In a real concurrent env, we'd use a Stored Procedure or RLS to prevent race conditions strictly.
    # For now, we trust the check above + immediate update.
    update_res = supabase.table("lands").update({"status": "reserved"}).eq("id", investment.land_id).execute()

    return inv_res.data[0]

@router.post("/confirm/{investment_id}", response_model=InvestmentResponse)
def confirm_investment(investment_id: str):
    # Admin calls this after receiving money
    
    # 1. Get Investment
    inv = supabase.table("investments").select("*").eq("id", investment_id).execute()
    if not inv.data:
        raise HTTPException(status_code=404, detail="Investment not found")
    investment = inv.data[0]

    # 2. Update Investment Status
    inv_update = supabase.table("investments").update({"status": "completed"}).eq("id", investment_id).execute()

    # 3. Update Land Status to 'active' (Sold)
    land_update = supabase.table("lands").update({"status": "active"}).eq("id", investment["land_id"]).execute()

    return inv_update.data[0]
