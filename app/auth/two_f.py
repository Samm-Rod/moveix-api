#app/auth/two_f.py
import pyotp
from app.utils.email import send_email_async

# Função para gerar segredo único por usuário (pode ser salvo no banco)
def generate_2fa_secret():
    return pyotp.random_base32()

# Função para enviar código 2FA (mock, pode ser email ou SMS)
async def send_2fa_code(user_email: str, code: str):
    subject = "Seu código de verificação Moveix"
    body = f"Seu código de verificação é: {code}"
    await send_email_async(subject, user_email, body)

# Função para validar código 2FA
def verify_2fa_code(secret: str, code: str) -> bool:
    return pyotp.TOTP(secret).verify(code, valid_window=4) # Aumenta a janela de validação para 4 códigos anteriores e futuros


# Função para gerar código 2FA para o usuário (caso precise gerar para debug)
def generate_2fa_code(secret: str) -> str:
    return pyotp.TOTP(secret).now()
