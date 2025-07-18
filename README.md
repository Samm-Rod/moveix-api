# 🚚 Moveix

Moveix é uma plataforma SaaS para gerenciamento de serviços de frete e mudanças, inspirada no modelo de aplicativos de mobilidade tipo Uber.  
O sistema conecta clientes que precisam transportar móveis e cargas a motoristas/fretes disponíveis, facilitando agendamento, pagamento e rastreamento em tempo real.

## 🛠️ Tecnologias

- 🐍 Backend: FastAPI (Python)
- 🐘 Banco de dados: PostgreSQL
- 🔐 Autenticação: JWT (JSON Web Tokens)
- 🐳 Containerização: Docker
- ☁️ Hospedagem: Railway claud
- 🗺️ Geolocalização: API Google Maps Platforms
- 🔁 Migração de dados: Alembic
- 🗃️ Controle de versão: GitHub
- 🔌 Comunicação em real-time: WebSockets( 🛠️ Em andamento)
- 💳 Gateway de pagamento: Asaas ( 🛠️ Em andamento)
- 🧠 Machine learning/Deep Learning : scikit-learn e torch ( 📅 Futuramente)

## 🚀 Funcionalidades principais

- 👤 Cadastro e autenticação de usuários e motoristas
- 📦 Criação, visualização e gerenciamento de pedidos de frete
- 🧾 Aceitação e finalização de corridas por motoristas
- 💰 Sistema de pagamento integrado (a implementar)
- 📘 API RESTful documentada com Swagger/OpenAPI

## 🎯 Objetivo

Fornecer uma solução escalável, segura e eficiente para o mercado de mudanças urbanas, com foco em usabilidade e automação, permitindo que usuários contratem serviços de forma rápida e confiável.

---

## 💻 Como rodar localmente

1. 📥 Clone o repositório:<br/>
   + `git clone git@github.com:Samm-Rod/moveix-api.git`
2. 🔧 Configure variáveis de ambiente para conexão com banco e JWT  
   + `python -m venv .venv`
   + `source .venv/bin/activate`
3. ▶️ Execute com Docker Compose ou diretamente com `uvicorn`<br/>  
   + Docker: `docker compose up --build` <br/>
   + Uvicorn: `uvicorn main.app:main --reload`<br/> 
4. 🔍 Acesse a API via `localhost` e utilize Swagger para testes
   + Link: `http://127.0.0.1:8000/` ou `http://localhost:8000/`
5. 🔍 Para manibular as feature vá até o Swagger do FastAPI
   + Link: `http://127.0.0.1:8000/docs` ou `http://localhost:8000/docs` 

---

## 🤝 Contribuição

Contribuições são bem-vindas via pull requests e issues.

---
<div align='center'>
    <img src="truck_moveix.gif" alt="Moveix" width="500">
</div>

## 📄 Licença

_Distribuído sob a MIT License. Veja LICENSE para mais informações._
