from sqlalchemy.orm import Session 
from app.models.driver import Driver
from app.utils.hashing import verify_password

def authenticate_driver(email: str, password: str, db: Session):

    driver = db.query(Driver).filter(Driver.email == email).first()

    if not driver:
        return None
    if not verify_password(password, driver.hashed_password):
        return None

    return driver

