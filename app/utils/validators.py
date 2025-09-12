from validate_docbr import CPF

cpf_validator = CPF()

def validate_cpf(cpf_number: str) -> bool:
    return cpf_validator.validate(cpf_number)

# def validate_cnpj(pj_number: str) -> bool:
#     return pj_validator.validate(pj_number)
#
# def validate_cnh(cnh_number: str) -> bool:
#     return cnh_validator.validate(cnh_number)