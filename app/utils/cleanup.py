
from datetime import datetime
from app.models.token import TokensBlacklist
from app.db.database import SessionLocal

def cleanup_expired_tokenss():
    """Remove tokenss expirados da blacklist"""
    db = SessionLocal()
    try:
        expired_tokenss = db.query(TokensBlacklist).filter(
            TokensBlacklist.expires_at < datetime.now()
        )
        count = expired_tokenss.count()
        expired_tokenss.delete()
        db.commit()
        print(f"Removidos {count} tokenss expirados da blacklist")
    finally:
        db.close()