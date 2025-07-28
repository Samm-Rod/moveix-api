import os
from fastapi import FastAPI, HTTPException, status 
from fastapi.security import HTTPBearer
from fastapi.middleware.cors import CORSMiddleware
from app.routes import client, driver, login, ride, vehicle, locations, payments, helper
from app.middleware.security_middleware import RestrictappMiddleware

# Definir se está em desenvolvimento
ENVIRONMENT = os.getenv("ENVIRONMENT", "production")

# Configurar Fastapi baseado no ambiente
if ENVIRONMENT == "development":
    app = FastAPI(
        title="Moveix api",
        description="api para o aplicativo Moveix",
        version="1.0.0",
        # Configurar autenticação no Swagger
        swagger_ui_parameters={
            "persistAuthorization": True,
            "displayRequestDuration": True,
        }
    )
else:
    app = FastAPI(
        docs_url=None, 
        redoc_url=None,
        title="Moveix api",
        description="api para o aplicativo Moveix", 
        version="1.0.0"
    )

# Configurar esquema de segurança
security = HTTPBearer()

# Middleware de segurança personalizada
app.add_middleware(RestrictappMiddleware)

# CORS para desenvolvimento e mobile apps
cors_origins = [
    "https://moveix.com",
    "capacitor://localhost",
]

if ENVIRONMENT == "development":
    cors_origins.extend([
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:4200",
        "http://localhost:8000",
    ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rota base
@app.get('/')
def read_root():
    return {'message': 'Hello, Moveix!'}

# Endpoint de health check
@app.get('/health')
def health_check():
    return {
        'status': 'healthy',
        'environment': ENVIRONMENT,
        'swagger_enabled': ENVIRONMENT == "development"
    }

# Endpoint para obter token de teste (apenas em desenvolvimento)
@app.post('/auth/test-token')
def get_test_token():
    if ENVIRONMENT != "development":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Not found num deu!"
        )

    
    return {
        "access_token": "test-token-for-swagger-development-only",
        "token_type": "bearer",
        "message": "Este é um token de teste para usar no Swagger"
    }

# Rotas com dependência de segurança explícita
app.include_router(client.router, prefix='/clients', tags=['Clients'])
app.include_router(driver.router, prefix='/drivers', tags=['Drivers'])
app.include_router(helper.router, prefix='/helpers', tags=['Helpers'])

app.include_router(ride.router, prefix='/ride', tags=['Rides'])
app.include_router(vehicle.router, prefix='/vehicles', tags=['Vehicles'])

app.include_router(locations.router, prefix='/maps', tags=['Maps'])

app.include_router(payments.router, prefix='/payments', tags=['Payments'])

app.include_router(login.router, prefix='/auth', tags=['Auth'])