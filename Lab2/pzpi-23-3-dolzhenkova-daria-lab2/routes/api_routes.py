from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from datetime import datetime
from services.db_service import SessionLocal
from models.models import AdvertisementDB, AnalyticsLogDB, FeedbackDB
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1", tags=["EmoAd System"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class AdCreate(BaseModel):
    emotion: str
    promo_code: str
    slogan: str

class FeedbackCreate(BaseModel):
    user_id: int
    ad_id: int
    rating: int
    comment: str = None

@router.post("/get_ad")
async def get_ad(data: dict, db: Session = Depends(get_db)):
    emotion = data.get('emotion', '').strip().lower()
    if not emotion:
        raise HTTPException(status_code=400, detail="Emotion is required")
    
    try:
        new_log = AnalyticsLogDB(selected_emotion=emotion, timestamp=str(datetime.now()), device_source="IoT-Terminal")
        db.add(new_log)
        db.commit()
    except:
        db.rollback()
    
    ad = db.query(AdvertisementDB).filter(AdvertisementDB.emotion == emotion).first()
    if not ad:
        raise HTTPException(status_code=404, detail="No ads found for this emotion")
    
    return {"promo_code": ad.promo_code, "slogan": ad.slogan}

@router.post("/user/feedback", status_code=status.HTTP_201_CREATED)
async def leave_feedback(feedback: FeedbackCreate, db: Session = Depends(get_db)):
    new_fb = FeedbackDB(**feedback.dict())
    db.add(new_fb)
    db.commit()
    return {"message": "Дякуємо за ваш відгук!"}

def verify_admin(x_role: str = Header("user")):
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Доступ дозволено лише адміністраторам")
    return True

@router.get("/admin/ads")
async def get_all_ads(db: Session = Depends(get_db), _: bool = Depends(verify_admin)):
    return db.query(AdvertisementDB).all()

@router.post("/admin/add_ad", status_code=status.HTTP_201_CREATED)
async def add_ad(ad: AdCreate, db: Session = Depends(get_db), _: bool = Depends(verify_admin)):
    new_ad = AdvertisementDB(emotion=ad.emotion.strip().lower(), promo_code=ad.promo_code, slogan=ad.slogan)
    db.add(new_ad)
    db.commit()
    db.refresh(new_ad)
    return {"message": "Успішно додано", "id": new_ad.id}

@router.delete("/admin/delete_ad/{ad_id}")
async def delete_ad(ad_id: int, db: Session = Depends(get_db), _: bool = Depends(verify_admin)):
    item = db.query(AdvertisementDB).filter(AdvertisementDB.id == ad_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Не знайдено")
    db.delete(item)
    db.commit()
    return {"message": "Успішно видалено"}