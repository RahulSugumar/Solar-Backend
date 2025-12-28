from fastapi import APIRouter, HTTPException, Depends, Header
from models import UserCreate, UserResponse, UserLogin
from database import supabase
from typing import Optional

router = APIRouter(prefix="/auth", tags=["Auth"])

# Mock session store for MVP (In producton use Redis or JWT)
# For this MVP, we will just return the User ID and User Object.
# The frontend can store user_id in localStorage.

@router.post("/register", response_model=UserResponse)
def register(user: UserCreate):
    existing = supabase.table("users").select("*").eq("email", user.email).execute()
    if existing.data:
        raise HTTPException(status_code=400, detail="Email already registered")

    # In a real app, hash password here.
    # We will store password for 'login' check (Simulated)
    # Note: Modify 'users' table to have 'password' column or ignore for demo if just using email.
    # Assuming user schema doesn't strict check extra fields yet, or we just rely on email for MVP demo uniqueness.
    
    response = supabase.table("users").insert({
        "email": user.email,
        "full_name": user.full_name,
        "phone": user.phone,
        "role": user.role,
        # "password": user.password # Uncomment if you add password column to Supabase
    }).execute()

    if not response.data:
        raise HTTPException(status_code=500, detail="Failed to create user")
    
    return response.data[0]

@router.post("/login", response_model=UserResponse)
def login(creds: UserLogin):
    # MVP: Check email. (password check skipped if DB doesn't have it, or matching if it does)
    response = supabase.table("users").select("*").eq("email", creds.email).execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = response.data[0]
    # if user.get('password') != creds.password: raise ...
    
    return user

@router.get("/me", response_model=UserResponse)
def get_me(user_id: str = Header(None, alias="X-User-ID")):
    # For MVP, we pass User ID in header "X-User-ID" as a simple auth mechanism
    if not user_id:
        raise HTTPException(status_code=401, detail="Missing User ID header")
        
    response = supabase.table("users").select("*").eq("id", user_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="User not found")
        
    return response.data[0]

@router.post("/logout")
def logout():
    return {"message": "Logged out successfully"}
