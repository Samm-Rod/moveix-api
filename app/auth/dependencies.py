from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.driver import Driver
from app.models.client import Client
from app.utils.config import SECRET_KEY, ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login')

# # Função para autenticar cliente
# def get_current_client(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail='Not authenticated as client',
#         headers={'WWW-Authenticate': 'Bearer'},
#     )
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         user_id = payload.get('sub')
#         role = payload.get('role')
#         if user_id is None or role != "client":
#             raise credentials_exception
#     except JWTError:
#         raise credentials_exception

#     client = db.query(Client).filter(Client.id == user_id).first()
#     if client is None:
#         raise credentials_exception
#     return {"role": role, "client": client}

# # Função para autenticar motorista
# def get_current_driver(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail='Not authenticated as driver',
#         headers={'WWW-Authenticate': 'Bearer'},
#     )
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         user_id = payload.get('sub')
#         role = payload.get('role')
#         if user_id is None or role != "driver":
#             raise credentials_exception
#     except JWTError:
#         raise credentials_exception

#     driver = db.query(Driver).filter(Driver.id == user_id).first()
#     if driver is None:
#         raise credentials_exception
#     return {"role": role, "driver": driver}


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
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
