from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from routers import auth, public, land_owner, investor, payment, admin

load_dotenv()

app = FastAPI(title="Solar Platform API", version="1.0.0")

# CORS Setup
origins = [
    "http://localhost:5173", # Vite Default
    "http://localhost:3000",
    "https://solarfrontend.netlify.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to Solar Energy Platform API"}

app.include_router(auth.router)
app.include_router(public.router)
app.include_router(land_owner.router)
app.include_router(investor.router)
app.include_router(admin.router) # New Admin Router
app.include_router(land_owner.router)
app.include_router(investor.router)
app.include_router(payment.router)
app.include_router(admin.router)
