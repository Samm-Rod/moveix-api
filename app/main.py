from fastapi import FastAPI
from app.routes import client
from app.routes import driver
from app.routes import client_login
from app.routes import driver_login
from app.routes import ride
from app.routes import vehicle

app = FastAPI()

@app.get('/')
def read_root():
    return {'message': 'Hello, Moveix!'}


app.include_router(client.router, prefix='/clients', tags=['Clients'])
app.include_router(driver.router, prefix='/drivers', tags=['Drivers'])

app.include_router(ride.router, prefix='/ride', tags=['Rides'])
app.include_router(vehicle.router, prefix='/vehicles', tags=['Vehicles'])

app.include_router(driver_login.router, prefix='/auth/driver', tags=['Auth'])
app.include_router(client_login.router, prefix='/auth/client', tags=['Auth'])