from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class UserDB(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default="user") 
    is_blocked = Column(Integer, default=0)

    sessions = relationship("UserSessionDB", back_populates="user")
    feedbacks = relationship("FeedbackDB", back_populates="user")

class AdvertisementDB(Base):
    __tablename__ = 'advertisements'
    id = Column(Integer, primary_key=True, index=True)
    emotion = Column(String(50), nullable=False)
    promo_code = Column(String(50), nullable=False)
    slogan = Column(String(255), nullable=False)

    feedbacks = relationship("FeedbackDB", back_populates="advertisement")

class AnalyticsLogDB(Base):
    __tablename__ = 'analytics_logs'
    log_id = Column(Integer, primary_key=True, index=True)
    selected_emotion = Column(String(50))
    timestamp = Column(String(50), default=str(datetime.now()))
    device_source = Column(String(50))

class UserSessionDB(Base):
    __tablename__ = 'user_sessions'
    session_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    login_time = Column(String(50), default=str(datetime.now()))
    ip_address = Column(String(50))
    status = Column(String(50), default="active")

    user = relationship("UserDB", back_populates="sessions")

class FeedbackDB(Base):
    __tablename__ = 'feedback'
    feedback_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    ad_id = Column(Integer, ForeignKey('advertisements.id'))
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)

    user = relationship("UserDB", back_populates="feedbacks")
    advertisement = relationship("AdvertisementDB", back_populates="feedbacks")