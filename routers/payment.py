from fastapi import APIRouter, HTTPException
from database import supabase

router = APIRouter(prefix="/payment", tags=["Payment"])

# 18. POST /payment/mark-paid
@router.post("/mark-paid")
def mark_payment_paid(investment_id: str):
    # Admin confirming backend payment manually
    # ideally guarded by Admin Check
    
    # 1. Update Investment
    inv_res = supabase.table("investments").update({"status": "completed"}).eq("id", investment_id).execute()
    if not inv_res.data:
        raise HTTPException(status_code=404, detail="Investment not found")
        
    investment = inv_res.data[0]
    
    # 2. Update Land to Active
    supabase.table("lands").update({"status": "active"}).eq("id", investment['land_id']).execute()
    
    return {"message": "Payment confirmed, Land is now Active"}
