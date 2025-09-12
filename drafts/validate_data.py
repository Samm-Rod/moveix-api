from validate_docbr import CPF
import logging

logger = logging.getLogger(__name__)
cpf = CPF()

def validate_cpf(cpf_number: str) -> bool:
    if not cpf.validate(cpf_number):
        logger.warning(f"CPF inválido : {my_cpf} !")
        return False
    logger.info(f"CPF válido : {my_cpf} !")
    return True


if __name__=="__main__":
    my_cpf = "000.000.000-00"
    result = validate_cpf(my_cpf)
    print(f"O CPF {my_cpf} é válido ? {result}")
