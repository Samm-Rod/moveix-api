from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.driver import Driver
from app.models.client import Client
from app.models.vehicle import Vehicle
from app.models.ride import Ride
from app.utils.config import SECRET_KEY, ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login')

def get_current_driver(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate':'Bearer'},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        driver_id = payload.get('sub')
        if driver_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if driver is None:
        raise credentials_exception
    return driver

def get_current_client(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate':'Bearer'},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        client_id = payload.get('sub')
        if client_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    client = db.query(Client).filter(Client.id == client_id).first()
    if client is None:
        raise credentials_exception
    return client


def get_current_ride(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate':'Bearer'},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        ride_id = payload.get('sub')
        if ride_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    ride = db.query(Ride).filter(Ride.id == ride_id).first()
    if ride is None:
        raise credentials_exception
    return ride