from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import DATABASE_URL

connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """FastAPI dependency for obtaining a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Creates all database tables, migrates missing columns, and seeds default records."""
    # 1. Run migrations for existing sqlite database if needed
    if "sqlite" in DATABASE_URL:
        import sqlite3
        from app.config import DB_PATH
        if DB_PATH.exists():
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            # check farmer_profiles columns
            cur.execute("PRAGMA table_info(farmer_profiles)")
            cols = {r[1] for r in cur.fetchall()}
            if cols and "created_at" not in cols:
                cur.execute("ALTER TABLE farmer_profiles ADD COLUMN created_at DATETIME")
            if cols and "updated_at" not in cols:
                cur.execute("ALTER TABLE farmer_profiles ADD COLUMN updated_at DATETIME")
            conn.commit()
            conn.close()

    import app.db.models  # ensure models are registered
    Base.metadata.create_all(bind=engine)

    # Seed default farmer profile if not exists
    db = SessionLocal()
    try:
        from app.db.models import FarmerProfile
        default = db.query(FarmerProfile).filter_by(farmer_id="default_farmer").first()
        if not default:
            profile = FarmerProfile(
                farmer_id="default_farmer",
                name="रामसिंह वर्मा (Ram Singh)",
                village="बख्शी का तालाब",
                district="Lucknow",
                state="Uttar Pradesh",
                farm_size_acres=3.5,
                current_crop="गेहूं",
                soil_type="जलोढ़ दोमट",
                irrigation_type="नहर व ट्यूबवेल",
                language="Hindi"
            )
            db.add(profile)
            db.commit()
    finally:
        db.close()
