from sqlalchemy.orm import Session
from app.models.helper import Helper
from app.utils.hashing import verify_password, hash_password
import logging
import sys

# Configuração do logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Handler para console
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)

# Formato dos logs
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# Adiciona o handler ao logger
if not logger.handlers:
    logger.addHandler(console_handler)

def authenticate_helper(email: str, password: str, db: Session):
    logger.info("=== INICIANDO AUTENTICAÇÃO DO HELPER ===")
    logger.info(f"Tentativa de login com email: {email}")
    
    try:
        helper = db.query(Helper).filter(Helper.email == email).first()
        logger.info(f"Query SQL: {str(db.query(Helper).filter(Helper.email == email))}")
        
        if helper:
            logger.info(f"Helper encontrado: ID={helper.id}, Email={helper.email}")
            logger.info(f"Hash da senha fornecida: {hash_password(password)}")
            logger.info(f"Hash da senha no banco: {helper.hashed_password}")
        else:
            logger.warning(f"Nenhum helper encontrado com o email: {email}")
            return None
    except Exception as e:
        logger.error(f"Erro ao autenticar helper: {str(e)}")
        return None
    
    if not verify_password(password, helper.hashed_password):
        print(f'Senha inválida para o helper: {helper.email}')
        return None
    
    print("Autenticação bem sucedida!")
    return helper
    
