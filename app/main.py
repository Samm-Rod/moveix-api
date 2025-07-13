from fastapi import FastAPI
from app.routes import client
from app.routes import driver
from app.routes import login
from app.routes import ride
from app.routes import vehicle
from app.routes import locations
from app.routes import payments

app = FastAPI()

@app.get('/')
def read_root():
    return {'message': 'Hello, Moveix!'}


app.include_router(client.router, prefix='/clients', tags=['Clients'])
app.include_router(driver.router, prefix='/drivers', tags=['Drivers'])

app.include_router(ride.router, prefix='/ride', tags=['Rides'])
app.include_router(vehicle.router, prefix='/vehicles', tags=['Vehicles'])

app.include_router(locations.router, prefix='/maps', tags=['Maps'])

app.include_router(payments.router, prefix='/payments', tags=['Payments'])


app.include_router(login.router, prefix='/auth', tags=['Auth'])