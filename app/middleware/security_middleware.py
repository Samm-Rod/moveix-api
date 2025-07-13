from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

PROTECTED_PREFIXES = ["/client", "/driver", "/ride", "/payments"]  # personalize com os seus endpoints privados
EXCLUDED_PATHS = ["/docs", "/openapi.json", "/health", "/login"]  # rotas públicas ou de login

class RestrictAPIMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Permite rotas públicas e estáticas
        if any(path.startswith(exclude) for exclude in EXCLUDED_PATHS):
            return await call_next(request)

        # Só bloqueia rotas privadas
        if any(path.startswith(protected) for protected in PROTECTED_PREFIXES):
            auth = request.headers.get("Authorization")
            if not auth or not auth.startswith("Bearer "):
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Esta API é restrita. Acesso não autorizado será registrado."}
                )

        return await call_next(request)
