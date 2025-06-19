# Moveix

Moveix é uma plataforma SaaS para gerenciamento de serviços de frete e mudanças, inspirada no modelo de aplicativos de mobilidade tipo Uber.  
O sistema conecta clientes que precisam transportar móveis e cargas a motoristas/fretes disponíveis, facilitando agendamento, pagamento e rastreamento em tempo real.

## Tecnologias

- Backend: FastAPI (Python)
- Banco de dados: PostgreSQL
- Autenticação: JWT (JSON Web Tokens)
- Containerização: Docker
- Hospedagem: Cloud (a definir)
- Controle de versão: GitHub

## Funcionalidades principais

- Cadastro e autenticação de usuários e motoristas
- Criação, visualização e gerenciamento de pedidos de frete
- Aceitação e finalização de corridas por motoristas
- Sistema de pagamento integrado (a implementar)
- API RESTful documentada com Swagger/OpenAPI

## Objetivo

Fornecer uma solução escalável, segura e eficiente para o mercado de mudanças urbanas, com foco em usabilidade e automação, permitindo que usuários contratem serviços de forma rápida e confiável.

---

## Como rodar localmente

1. Clone o repositório  
2. Configure variáveis de ambiente para conexão com banco e JWT  
3. Execute com Docker Compose ou diretamente com `uvicorn`  
4. Acesse a API via `localhost` e utilize Swagger para testes

---

## Contribuição

Contribuições são bem-vindas via pull requests e issues.

---

## Licença

MIT License
