#app/auth/two_f.py
import pyotp
import time
from typing import Tuple

# Função para gerar segredo único por usuário (pode ser salvo no banco)
def generate_2fa_secret() -> str:
    return pyotp.random_base32()

# Função para gerar código 2FA - retorna o código e o tempo restante
def generate_2fa_code(secret: str) -> Tuple[str, int]:
    totp = pyotp.TOTP(secret)
    return totp.now(), totp.interval - int(time.time()) % totp.interval

# Função para validar código 2FA
def verify_2fa_code(secret: str, code: str) -> bool:
    return pyotp.TOTP(secret).verify(code, valid_window=1)  # 30 segundos antes e depois

# Mock da função de envio para manter compatibilidade com código existente
async def send_2fa_code(user_email: str, code: str):
    # Em produção, você pode implementar o envio por SMS ou outro método
    print(f"[DEBUG] 2FA code for {user_email}: {code}")
    return True
