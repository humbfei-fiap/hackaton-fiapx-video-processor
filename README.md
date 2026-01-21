# FIAP X - Sistema de Processamento de Vídeos

Este projeto foi desenvolvido como parte do desafio da FIAP X. O sistema permite que usuários façam upload de vídeos, que são processados de forma assíncrona para extrair frames (1 frame por segundo) e gerar um arquivo ZIP para download.

## 🏗️ Arquitetura

O sistema utiliza **Arquitetura de Microsserviços** e segue os princípios da **Clean Architecture (Hexagonal)** para garantir desacoplamento e testabilidade.

### Componentes:
- **API Gateway (FastAPI):** Responsável pela autenticação (JWT), recebimento de vídeos e consulta de status.
- **Video Worker (Python + OpenCV):** Processa os vídeos da fila e gera o ZIP de frames.
- **Mensageria (RabbitMQ):** Orquestra o processamento assíncrono.
- **Banco de Dados (PostgreSQL):** Persiste dados de usuários, metadados de vídeos e status.
- **Storage Compartilhado:** Volume usado para troca de arquivos entre Gateway e Worker.

## 🚀 Como Executar Localmente (Docker Compose)

1. Certifique-se de ter Docker e Docker Compose instalados.
2. Na raiz do projeto, execute:
   ```bash
   docker-compose up --build
   ```
3. Acesse a API em `http://localhost:8000`.
4. Documentação interativa (Swagger): `http://localhost:8000/docs`.

## ☸️ Kubernetes (Deploy EKS/Local)

Os manifestos estão na pasta `/k8s`. Para aplicar:

1. Crie o namespace e configurações base:
   ```bash
   kubectl apply -f k8s/infra/configs.yaml
   kubectl apply -f k8s/infra/pvc.yaml
   ```
2. Suba a infra:
   ```bash
   kubectl apply -f k8s/infra/postgres.yaml
   kubectl apply -f k8s/infra/rabbitmq.yaml
   ```
3. Suba as aplicações:
   ```bash
   kubectl apply -f k8s/app/gateway/deploy.yaml
   kubectl apply -f k8s/app/worker/deploy.yaml
   ```

## 🧪 Testes

Foram implementados testes unitários focados nos **Casos de Uso** (Regras de Negócio), garantindo a qualidade sem depender de infraestrutura externa.

Para rodar os testes manualmente:
```bash
cd app/gateway && pytest
cd app/worker && pytest
```

## 🔄 CI/CD

O projeto conta com um pipeline no **GitHub Actions** que:
1. Executa testes unitários em cada Push/PR.
2. Realiza o Build das imagens Docker para garantir que o código está pronto para deploy.
