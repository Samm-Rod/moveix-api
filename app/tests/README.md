# Testes da Aplicação Moveix

Este diretório contém todos os testes da aplicação Moveix, organizados por categoria.

## Estrutura dos Testes

```
app/tests/
├── conftest.py              # Configuração do pytest e fixtures
├── test_payments.py         # Testes específicos de pagamentos
├── test_services.py         # Testes de todos os services
├── test_routes.py           # Testes de todas as routes
├── test_integration.py      # Testes de integração
└── README.md               # Esta documentação
```

## Tipos de Testes

### 1. Testes de Services (`test_services.py`)
Testa todas as funções de negócio da aplicação:
- ✅ Criação, leitura, atualização e exclusão de clientes
- ✅ Criação, leitura, atualização e exclusão de motoristas
- ✅ Criação, leitura, atualização e exclusão de veículos
- ✅ Criação, leitura, atualização e exclusão de corridas
- ✅ Criação, leitura, atualização e exclusão de pagamentos
- ✅ Criação, leitura, atualização e exclusão de localizações
- ✅ Autenticação de clientes e motoristas
- ✅ Operações específicas de corrida (aceitar, iniciar, finalizar)

### 2. Testes de Routes (`test_routes.py`)
Testa todos os endpoints da app:
- ✅ Endpoints de clientes (CRUD completo)
- ✅ Endpoints de motoristas (CRUD completo)
- ✅ Endpoints de veículos (CRUD completo)
- ✅ Endpoints de corridas (CRUD completo)
- ✅ Endpoints de pagamentos (CRUD completo)
- ✅ Endpoints de localizações (CRUD completo)
- ✅ Endpoints de autenticação (login cliente/motorista)
- ✅ Tratamento de erros (404, 422, 401)

### 3. Testes de Integração (`test_integration.py`)
Testa fluxos completos da aplicação:
- ✅ Fluxo completo de corrida (cliente → motorista → veículo → corrida → pagamento)
- ✅ Registro e login via app
- ✅ Cenários de erro e validação
- ✅ Testes de performance básicos

### 4. Testes Específicos (`test_payments.py`)
Testes específicos para funcionalidades críticas:
- ✅ Criação de pagamentos
- ✅ Validação de dados
- ✅ Integração com serviços externos

## Como Executar os Testes

### Opção 1: Usando o script personalizado
```bash
# Executar todos os testes
python run_tests.py

# Executar um teste específico
python run_tests.py payments
python run_tests.py services
python run_tests.py routes
python run_tests.py integration
python run_tests.py all
```

### Opção 2: Usando pytest diretamente
```bash
# Executar todos os testes
python -m pytest app/tests/ -v

# Executar um arquivo específico
python -m pytest app/tests/test_payments.py -v
python -m pytest app/tests/test_services.py -v
python -m pytest app/tests/test_routes.py -v
python -m pytest app/tests/test_integration.py -v

# Executar uma classe específica
python -m pytest app/tests/test_services.py::TestClientServices -v

# Executar um método específico
python -m pytest app/tests/test_services.py::TestClientServices::test_create_client_success -v
```

### Opção 3: Com cobertura de código
```bash
# Instalar pytest-cov se não estiver instalado
pip install pytest-cov

# Executar com cobertura
python -m pytest app/tests/ --cov=app --cov-report=html
```

## Configuração dos Testes

### Banco de Dados de Teste
Os testes usam um banco SQLite em memória configurado em `conftest.py`:
- ✅ Isolamento completo entre testes
- ✅ Limpeza automática após cada teste
- ✅ Performance otimizada

### Fixtures Disponíveis
- `db`: Sessão do banco de dados para cada teste
- `setup_database`: Configuração inicial do banco

## Estrutura de um Teste

```python
def test_exemplo_success(self, db: Session):
    """Testa funcionalidade com sucesso"""
    
    # 1. Preparar dados
    client_data = ClientCreate(
        name="Teste",
        email="teste@email.com",
        password="senha123"
    )
    
    # 2. Executar ação
    result = create_client(client_data, db)
    
    # 3. Verificar resultado
    assert result.name == "Teste"
    assert result.email == "teste@email.com"
    assert result.id is not None
```

## Boas Práticas

### ✅ O que fazer:
- Use nomes descritivos para os testes
- Teste casos de sucesso e erro
- Use fixtures para dados comuns
- Isole cada teste (não dependa de outros)
- Verifique múltiplos aspectos do resultado

### ❌ O que evitar:
- Testes que dependem de outros
- Dados hardcoded desnecessários
- Testes muito complexos (quebre em menores)
- Asserções muito específicas
- Mocks desnecessários

## Cobertura de Testes

### Services Testados:
- [x] `auth.py` - Autenticação geral
- [x] `auth_client.py` - Autenticação de clientes
- [x] `auth_driver.py` - Autenticação de motoristas
- [x] `client.py` - Gerenciamento de clientes
- [x] `driver.py` - Gerenciamento de motoristas
- [x] `vehicle.py` - Gerenciamento de veículos
- [x] `ride.py` - Gerenciamento de corridas
- [x] `payments.py` - Gerenciamento de pagamentos
- [x] `locations.py` - Gerenciamento de localizações

### Routes Testadas:
- [x] `client.py` - Endpoints de clientes
- [x] `driver.py` - Endpoints de motoristas
- [x] `vehicle.py` - Endpoints de veículos
- [x] `ride.py` - Endpoints de corridas
- [x] `payments.py` - Endpoints de pagamentos
- [x] `locations.py` - Endpoints de localizações
- [x] `login.py` - Endpoints de autenticação geral
- [x] `client_login.py` - Login de clientes
- [x] `driver_login.py` - Login de motoristas

## Troubleshooting

### Erro: "Column[int] cannot be assigned to parameter"
**Solução:** Adicione `# type: ignore` nos locais onde o type checker não reconhece objetos SQLAlchemy.

### Erro: "Database is locked"
**Solução:** Verifique se não há outras instâncias da aplicação rodando.

### Erro: "Module not found"
**Solução:** Certifique-se de estar no diretório raiz do projeto ao executar os testes.

## Contribuindo

Ao adicionar novos testes:
1. Siga a estrutura existente
2. Use nomes descritivos
3. Teste casos de sucesso e erro
4. Documente funcionalidades complexas
5. Execute todos os testes antes de commitar 