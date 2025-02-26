from pydantic import BaseModel,EmailStr,constr
from typing import Optional,Annotated,List

class UserCreate(BaseModel):
    username:str
    email:EmailStr
    password: Annotated[str,constr(min_length=8)]
    referral_code:Optional[str]=None
    
class UserResponse(BaseModel):
    id:int
    username:str
    email:str
    referral_code:str
    referred_by:Optional[str]=None

    class config:
        orm_mode=True
class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: Annotated[str,constr(min_length=8)]

class ReferralStatsResponse(BaseModel):
    referral_count: int
    referrals: List[str]