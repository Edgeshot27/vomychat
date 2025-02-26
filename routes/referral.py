from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from data.databse import get_db
from data.models import User
from typing import List
from data.schemas import ReferralStatsResponse
router = APIRouter()

@router.get("/stats", response_model=ReferralStatsResponse)
async def referral_stats(referral_code: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.referred_by == referral_code))
    referrals = result.scalars().all()
    referral_usernames = [user.username for user in referrals]
    return {"referral_count": len(referrals), "referrals": referral_usernames}
