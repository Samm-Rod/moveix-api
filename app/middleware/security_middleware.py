import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
import os

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RestrictAPIMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        
        # Configurações do middleware
        self.protected_prefixes = {
            "/clients",
            "/drivers",  
            "/ride",
            "/vehicles",
            "/maps",
            "/payments"
        }
        
        self.excluded_paths = {
            "/",
            "/health",
            "/favicon.ico",
            "/openapi.json",
            "/docs",
            "/redoc",
            "/auth",
            "/static"
        }
        
        # Rate limiting simples
        self.request_counts = {}
        self.rate_limit_window = 60  # 1 minuto
        self.max_requests_per_minute = 100
        
        # Ambiente
        self.environment = os.getenv("ENVIRONMENT", "production").lower()
        if self.environment == "development":
            logger.warning("⚠️ Executando em modo DEVELOPMENT - Middleware de segurança com restrições reduzidas ⚠️")
        
    def _is_excluded_path(self, path: str) -> bool:
        """Verifica se o path está nas rotas excluídas"""
        # Verifica caminhos exatos
        if path in {"/", "/health", "/favicon.ico", "/openapi.json"}:
            return True
        
        # Verifica prefixos de caminho
        return any(
            path.startswith(excluded_path)
            for excluded_path in {"/docs", "/redoc", "/auth", "/static"}
        )
    
    def _is_protected_path(self, path: str) -> bool:
        """Verifica se o path está nas rotas protegidas"""
        return any(path.startswith(protected) for protected in self.protected_prefixes)
    
    def _get_client_ip(self, request: Request) -> str:
        """Extrai o IP do cliente considerando proxies"""
        x_forwarded_for = request.headers.get("X-Forwarded-For")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        
        x_real_ip = request.headers.get("X-Real-IP")
        if x_real_ip:
            return x_real_ip
        
        return request.client.host if request.client else "unknown"
    
    def _check_rate_limit(self, client_ip: str) -> bool:
        """Implementa rate limiting básico"""
        current_time = time.time()
        
        # Limpar entradas antigas
        self.request_counts = {
            ip: (count, timestamp) for ip, (count, timestamp) in self.request_counts.items()
            if current_time - timestamp < self.rate_limit_window
        }
        
        # Verificar rate limit para este IP
        if client_ip in self.request_counts:
            count, timestamp = self.request_counts[client_ip]
            if current_time - timestamp < self.rate_limit_window:
                if count >= self.max_requests_per_minute:
                    return False
                self.request_counts[client_ip] = (count + 1, timestamp)
            else:
                self.request_counts[client_ip] = (1, current_time)
        else:
            self.request_counts[client_ip] = (1, current_time)
        
        return True
    
    def _log_security_event(self, event_type: str, request: Request, details: str = ""):
        """Log eventos de segurança"""
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("User-Agent", "Unknown")
        
        logger.warning(
            f"SECURITY_EVENT: {event_type} | "
            f"IP: {client_ip} | "
            f"Path: {request.url.path} | "
            f"Method: {request.method} | "
            f"User-Agent: {user_agent} | "
            f"Details: {details}"
        )
    
    def _validate_auth_token(self, auth_header: str) -> bool:
        """Validação básica do token"""
        if not auth_header or not auth_header.startswith("Bearer "):
            return False
        
        token = auth_header.replace("Bearer ", "").strip()
        
        # Em desenvolvimento, aceitar token de teste
        if self.environment == "development" and token == "test-token-for-swagger-development-only":
            return True
        
        # Validações básicas
        if len(token) < 10:  # Token muito curto
            return False
        
        # Aqui você pode adicionar validações mais complexas
        return True
    
    async def dispatch(self, request: Request, call_next):
        client_ip = self._get_client_ip(request)
        path = request.url.path
        
        if self.environment == "development":
            if any(path.startswith(p) for p in ["/docs", "/redoc", "/openapi.json", "/static"]):
                return await call_next(request)

        # Log para debug em desenvolvimento
        if self.environment == "development":
            logger.info(f"Processing request to {path} from {client_ip}")
        
        # 1. Permite rotas públicas
        if self._is_excluded_path(path):
            if self.environment == "development":
                logger.info(f"Path {path} is excluded from security checks")
            return await call_next(request)
        
        # 2. Rate limiting (aplica a todas as rotas não excluídas)
        if not self._check_rate_limit(client_ip):
            self._log_security_event("RATE_LIMIT_EXCEEDED", request)
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Try again later."}
            )
        
        # 3. Verifica rotas protegidas
        if self._is_protected_path(path):
            auth = request.headers.get("Authorization")
            
            if not self._validate_auth_token(auth):
                self._log_security_event(
                    "UNAUTHORIZED_ACCESS_ATTEMPT", 
                    request, 
                    f"Missing or invalid auth token"
                )
                return JSONResponse(
                    status_code=401,
                    content={
                        "detail": "Esta API é restrita. Acesso não autorizado será registrado.",
                        "error_code": "UNAUTHORIZED_ACCESS"
                    }
                )
        
        # 4. Verificações adicionais de segurança em produção
        if self.environment == "production":
            user_agent = request.headers.get("User-Agent", "")
            suspicious_agents = ["curl", "wget", "python-requests", "bot", "crawler"]
            
            if any(agent in user_agent.lower() for agent in suspicious_agents):
                self._log_security_event("SUSPICIOUS_USER_AGENT", request, f"User-Agent: {user_agent}")
                return JSONResponse(
                    status_code=403,
                    content={"detail": "Access forbidden"}
                )
            
            # Verificar Content-Type para requests POST/PUT
            if request.method in ["POST", "PUT", "PATCH"]:
                content_type = request.headers.get("Content-Type", "")
                if not content_type.startswith("application/json"):
                    self._log_security_event("INVALID_CONTENT_TYPE", request, f"Content-Type: {content_type}")
                    return JSONResponse(
                        status_code=400,
                        content={"detail": "Content-Type must be application/json"}
                    )
        
        # Log de acesso bem-sucedido (apenas para rotas protegidas)
        if self._is_protected_path(path):
            logger.info(f"AUTHORIZED_ACCESS: {client_ip} -> {request.method} {path}")
        
        return await call_next(request)