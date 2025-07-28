
from datetime import datetime
from app.models.token import TokenBlacklist
from app.db.database import SessionLocal

def cleanup_expired_tokens():
    """Remove tokens expirados da blacklist"""
    db = SessionLocal()
    try:
        expired_tokens = db.query(TokenBlacklist).filter(
            TokenBlacklist.expires_at < datetime.now()
        )
        count = expired_tokens.count()
        expired_tokens.delete()
        db.commit()
        print(f"Removidos {count} tokens expirados da blacklist")
    finally:
        db.close()