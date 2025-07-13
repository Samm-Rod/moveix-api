from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import client, driver, login, ride, vehicle, locations, payments
from app.middleware.security_middleware import RestrictAPIMiddleware

app = FastAPI(docs_url=None, redoc_url=None)  # desativa /docs e /redoc

# CORS para desenvolvimento e mobile apps (ajuste conforme necessidade)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React local
        "https://moveix.com",     # seu domínio final
        "capacitor://localhost",  # mobile
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware de segurança personalizada (opcional)
app.add_middleware(RestrictAPIMiddleware)

# Rota base
@app.get('/')
def read_root():
    return {'message': 'Hello, Moveix!'}

# Rotas
app.include_router(client.router, prefix='/clients', tags=['Clients'])
app.include_router(driver.router, prefix='/drivers', tags=['Drivers'])
app.include_router(ride.router, prefix='/ride', tags=['Rides'])
app.include_router(vehicle.router, prefix='/vehicles', tags=['Vehicles'])
app.include_router(locations.router, prefix='/maps', tags=['Maps'])
app.include_router(payments.router, prefix='/payments', tags=['Payments'])
app.include_router(login.router, prefix='/auth', tags=['Auth'])
