from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from datetime import datetime
from services.db_service import SessionLocal
from models.models import AdvertisementDB, AnalyticsLogDB, FeedbackDB, UserDB
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1", tags=["EmoAd Full System"])

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

@router.get("/user/feedbacks/{user_id}")
async def get_user_feedbacks(user_id: int, db: Session = Depends(get_db)):
    return db.query(FeedbackDB).filter(FeedbackDB.user_id == user_id).all()



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

@router.get("/admin/analytics/summary")
async def get_analytics_summary(db: Session = Depends(get_db), _: bool = Depends(verify_admin)):
    logs = db.query(AnalyticsLogDB).all()
    total_clicks = len(logs)
    if total_clicks == 0:
        return {"total_interactions": 0, "emotion_distribution": {}}
    
    emotion_counts = {}
    for log in logs:
        emo = log.selected_emotion
        emotion_counts[emo] = emotion_counts.get(emo, 0) + 1
        
    distribution = {
        emo: {"count": count, "percentage": round((count / total_clicks) * 100, 2)}
        for emo, count in emotion_counts.items()
    }
    return {"total_interactions": total_clicks, "emotion_distribution": distribution}

@router.get("/admin/ads/performance")
async def get_ads_performance(db: Session = Depends(get_db), _: bool = Depends(verify_admin)):
    ads = db.query(AdvertisementDB).all()
    report = []
    for ad in ads:
        feedbacks = db.query(FeedbackDB).filter(FeedbackDB.ad_id == ad.id).all()
        ratings = [f.rating for f in feedbacks]
        avg_rating = round(sum(ratings) / len(ratings), 2) if ratings else 0.0
        report.append({
            "ad_id": ad.id, "slogan": ad.slogan, "emotion": ad.emotion,
            "total_reviews": len(ratings), "average_rating": avg_rating
        })
    return report

@router.get("/admin/export/backup")
async def export_system_data(db: Session = Depends(get_db), _: bool = Depends(verify_admin)):
    ads = db.query(AdvertisementDB).all()
    logs = db.query(AnalyticsLogDB).all()
    users = db.query(UserDB).all()
    return {
        "export_timestamp": str(datetime.now()),
        "advertisements_count": len(ads),
        "logs_count": len(logs),
        "data": {
            "advertisements": [{"id": a.id, "emotion": a.emotion, "slogan": a.slogan} for a in ads]
        }
    }

@router.patch("/admin/users/{user_id}/block")
async def toggle_user_block(user_id: int, db: Session = Depends(get_db), _: bool = Depends(verify_admin)):
    user = db.query(UserDB).filter(UserDB.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")
    user.is_blocked = 1 if user.is_blocked == 0 else 0
    db.commit()
    return {"message": f"Статус блокування змінено", "user_id": user.user_id, "is_blocked": user.is_blocked}