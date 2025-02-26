import os
from fastapi import FastAPI, BackgroundTasks
from routes import auth, referral
from data.databse import init_db
from data.models import Base
from fastapi.security import OAuth2PasswordBearer
# Initialize FastAPI
app = FastAPI()

@app.on_event("startup")
async def startup():
    await init_db()

# Include routes
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(referral.router, prefix="/api/referrals", tags=["Referrals"])
