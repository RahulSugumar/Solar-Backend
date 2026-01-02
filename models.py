from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID

# --- Wrapper Models ---
# For standardizing responses if needed, but we'll stick to direct models for simplicity as per MVP.

# --- User Models ---
class UserBase(BaseModel):
    email: str
    full_name: str
    phone: Optional[str] = None
    role: str = "investor" # 'land_owner', 'investor', 'admin'
    balance: float = 0.0

class UserCreate(UserBase):
    password: str # In real app, hash this. For MVP demo, plain or simple hash.

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(UserBase):
    id: str
    created_at: datetime

# --- Land Models ---
class LandBase(BaseModel):
    title: str # User gives a name/title
    location: str
    land_type: str # e.g. "Rooftop", "Open Land", "Farm"
    ownership_info: str # e.g. "Sole Owner", "Leased", etc.
    area_sqft: float
    total_price: float
    potential_capacity_kw: float = 0.0 # e.g. 5kW, 10kW
    # Payout info for Land Owner
    owner_fixed_payout: float = 0.0
    owner_revenue_share_percent: float = 0.0
    description: Optional[str] = None
    image_url: Optional[str] = None
    status: str = "available" # 'available', 'reserved', 'active', 'pending_approval'

class LandCreate(LandBase):
    owner_id: str

class LandResponse(LandBase):
    id: str
    owner_id: str
    created_at: datetime

# --- Investment Models ---
class InvestmentCreate(BaseModel):
    land_id: str
    investor_id: str
    amount: float

class InvestmentResponse(InvestmentCreate):
    id: str
    status: str # 'pending', 'completed', 'cancelled'
    transaction_date: datetime

# --- Stats Models ---
class PlatformStats(BaseModel):
    total_investors: int
    total_land_owners: int
    active_sites: int
    total_energy_generated: float # Mock value or sum
