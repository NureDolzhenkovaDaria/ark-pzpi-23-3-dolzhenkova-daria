import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.models import Base, AdvertisementDB

DB_FILE = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "emo_ad_extended.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{os.path.abspath(DB_FILE)}"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    try:
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        if db.query(AdvertisementDB).count() == 0:
            sample_ads = [
                AdvertisementDB(emotion='happy', promo_code='HAPPY2026', slogan='Чудовий настрій!'),
                AdvertisementDB(emotion='sad', promo_code='SUPPORT25', slogan='Тримайся! Все налагодиться.'),
                AdvertisementDB(emotion='tired', promo_code='COFFEE50', slogan='Втомився? Час випити кави зі знижкою!'),
                AdvertisementDB(emotion='angry', promo_code='CHILL77', slogan='Видихни. Час для спокою.')
            ]
            db.add_all(sample_ads)
            db.commit()
            print("[INIT] База успішно заповнена рекламами!")
    except Exception as e:
        print(f"[INIT ERROR]: {e}")
    finally:
        db.close()