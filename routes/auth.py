from data.databse import get_db
from data.models import User
from data.schemas import UserCreate, UserResponse, ForgotPasswordRequest, ResetPasswordRequest,ReferralStatsResponse
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import random, string
import jwt
import datetime
from passlib.context import CryptContext
from config import KEY, algorithm
import secrets
from sqlalchemy.future import select
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm,OAuth2AuthorizationCodeBearer
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token") 



def generate_referral_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def hashed(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: datetime.timedelta):
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, KEY, algorithm=algorithm)


@router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    existing_user = await db.execute(select(User).where(User.email == user.email))
    if existing_user.scalar():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already in use",
        )

    hashed_password = hashed(user.password)
    random_number = random.randint(1000, 9999)
    referral_code = f"ref_{user.username}_{random_number}"

    # Verify that the referral code provided (if any) belongs to an existing user
    referred_by = None
    if user.referral_code:
        referring_user = await db.execute(select(User).where(User.referral_code == user.referral_code))
        if referring_user.scalar():
            referred_by = user.referral_code
        else:
            raise HTTPException(status_code=400, detail="Invalid referral code")

    new_user = User(
        username=user.username,
        email=user.email,
        password_hash=hashed_password,
        referral_code=referral_code,
        referred_by=referred_by,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user




@router.post("/login")
async def login(username: str, password: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar()
    
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    
    access_token = create_access_token(data={"sub": user.username}, expires_delta=datetime.timedelta(hours=24))
    return {"access_token": access_token, "token_type": "bearer"}




@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar()  # ✅ Fix: Correct `.scalar()`
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    reset_token = secrets.token_urlsafe(32)
    user.reset_token = reset_token
    await db.commit()
    return {"message": "Reset token generated", "reset_token": reset_token}


@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.reset_token == request.token))
    user = result.scalar()  # ✅ Fix: Correct `.scalar()`
    
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")

    user.password_hash = hashed(request.new_password)
    user.reset_token = None
    await db.commit()
    return {"message": "Password reset successful"}


async def get_current_user(
    token: str = Depends(oauth2_scheme),  # ✅ Get token from header
    db: AsyncSession = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, KEY, algorithms=[algorithm])
        username: str = payload.get("sub")
        if not username:
            raise credentials_exception
    except Exception as e:
        raise credentials_exception
    
    # Get user from database
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar()
    if not user:
        raise credentials_exception
        
    return user

@router.get("/users/referred", response_model=ReferralStatsResponse)
async def get_referred_users(
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    """
    Get a list of users referred by the authenticated user.
    """
    result = await db.execute(select(User).where(User.referred_by == current_user.referral_code))
    referred_users = result.scalars().all()

    return {
        "referral_count": len(referred_users),
        "referrals": [user.username for user in referred_users]
    }

