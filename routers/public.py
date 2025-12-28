from fastapi import APIRouter
from models import LandResponse, PlatformStats
from database import supabase
from typing import List

router = APIRouter(tags=["Public"])

# 5. GET /map/solar-sites
@router.get("/map/solar-sites", response_model=List[LandResponse])
def get_active_sites():
    # 'active' means installed/sold
    response = supabase.table("lands").select("*").eq("status", "active").execute()
    return response.data

# 6. GET /stats/platform
@router.get("/stats/platform", response_model=PlatformStats)
def get_platform_stats():
    # Count users
    users_res = supabase.table("users").select("role", count="exact").execute()
    # This is a bit manual in Supabase-py without direct count queries sometimes, 
    # but let's try fetching all or using robust counting if available.
    # For MVP with low data, fetching * is fine.
    
    all_users = supabase.table("users").select("role").execute().data
    all_lands = supabase.table("lands").select("status").execute().data
    
    investors = len([u for u in all_users if u['role'] == 'investor'])
    owners = len([u for u in all_users if u['role'] == 'land_owner'])
    active_sites = len([l for l in all_lands if l['status'] == 'active'])
    
    # Mocking energy for now as we don't have generation data table yet
    total_energy = active_sites * 1250.5 # Random multiplier
    
    return {
        "total_investors": investors,
        "total_land_owners": owners,
        "active_sites": active_sites,
        "total_energy_generated": total_energy
    }

# 7. GET /lands/available
@router.get("/lands/available", response_model=List[LandResponse])
def get_available_lands():
    response = supabase.table("lands").select("*").eq("status", "available").execute()
    return response.data
