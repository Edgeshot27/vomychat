from sqlalchemy import Column,Integer,String,ForeignKey,DateTime
from sqlalchemy.orm import relationship
from .databse import Base
from datetime import datetime
class User(Base):
    __tablename__="users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    referral_code = Column(String, unique=True)
    referred_by = Column(String, ForeignKey("users.referral_code"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    referrals = relationship("User", backref="referrer", remote_side=[referral_code])

