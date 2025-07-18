from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.driver import Driver
from app.models.client import Client
from app.utils.config import SECRET_KEY, ALGORITHM

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login')

security = HTTPBearer()

def get_current_user(token: str = Depends(security), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Not authenticated',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get('sub')
        role = payload.get('role')
        if user_id is None or role not in ("client", "driver"):
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    if role == "client":
        user = db.query(Client).filter(Client.id == user_id).first()
    elif role == "driver":
        user = db.query(Driver).filter(Driver.id == user_id).first()
    else:
        raise credentials_exception

    if user is None:
        raise credentials_exception

    return {"role": role, "user": user}
