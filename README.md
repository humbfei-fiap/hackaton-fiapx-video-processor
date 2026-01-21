# FIAP X - Sistema de Processamento de Vídeos

Este projeto foi desenvolvido como parte do desafio da FIAP X (Hackathon SOAT). O sistema permite que usuários façam upload de vídeos, que são processados de forma assíncrona para extrair frames e gerar um arquivo ZIP para download.

## 🏗️ Arquitetura e Desenho da Solução

O sistema segue o padrão de **Microsserviços** com comunicação assíncrona, estruturado internamente com **Clean Architecture (Hexagonal)** para garantir desacoplamento, testabilidade e fácil manutenção.

### Diagrama da Arquitetura (Mermaid)

```mermaid
graph TD
    User((Usuário))
    
    subgraph "Camada de Entrada (BFF)"
        Gateway[API Gateway<br/>(FastAPI)]
    end
    
    subgraph "Persistência & Mensageria"
        DB[(PostgreSQL)]
        Redis[(Redis Cache)]
        Queue[[RabbitMQ]]
        Storage{Shared Volume<br/>(EFS/PVC)}
    end
    
    subgraph "Processamento Assíncrono"
        Worker[Video Worker<br/>(Python/OpenCV)]
        SES[AWS SES<br/>(Email)]
    end

    %% Fluxo de Upload
    User -->|1. Upload Vídeo + Auth| Gateway
    Gateway -->|2. Salva Arquivo| Storage
    Gateway -->|3. Registra PENDING| DB
    Gateway -->|4. Publica Mensagem| Queue

    %% Fluxo de Processamento
    Queue -->|5. Consome Tarefa| Worker
    Worker -->|6. Lê Arquivo| Storage
    Worker -->|7. Processa Frames & ZIP| Worker
    Worker -->|8. Salva ZIP| Storage
    Worker -->|9. Atualiza COMPLETED| DB
    Worker -.->|10. Notifica Erro (se houver)| SES

    %% Fluxo de Leitura (Status)
    User -->|11. Consulta Status| Gateway
    Gateway -->|12. Check Cache| Redis
    Redis -.->|Miss| DB
    Redis -.->|Hit| Gateway
    Gateway -->|13. Retorna Status/Link| User
```

### Componentes

1.  **API Gateway (BFF):**
    *   **Função:** Ponto único de entrada. Gerencia autenticação (JWT) e validação.
    *   **Tecnologia:** Python (FastAPI).
    *   **Padrões:** Cache-Aside (Redis) para otimizar leitura de status.

2.  **Message Broker (RabbitMQ):**
    *   **Função:** Desacopla o recebimento do processamento. Garante que picos de tráfego não derrubem o processamento.
    *   **Resiliência:** Mensagens são persistentes (Durable Queues).

3.  **Video Worker:**
    *   **Função:** Processamento pesado (CPU Bound). Extrai frames usando OpenCV.
    *   **Tecnologia:** Python.
    *   **Design:** Implementa Clean Architecture com Adaptadores para Notificação (Strategy Pattern: Log Local vs AWS SES).

4.  **Armazenamento:**
    *   **PostgreSQL:** Dados transacionais (Usuários, Metadados).
    *   **Redis:** Cache de curto prazo para aliviar o banco em consultas repetitivas de status.
    *   **Shared Volume:** Armazenamento de arquivos grandes (Vídeos/ZIPs).

## 🚀 Como Executar Localmente

### Pré-requisitos
*   Docker e Docker Compose instalados.

### Passo a Passo
1.  **Suba o ambiente:**
    ```bash
    docker-compose up --build --force-recreate
    ```
    *(O `--force-recreate` é recomendado na primeira execução para garantir a criação correta das tabelas do banco)*.

2.  **Acesse a Documentação (Swagger):**
    Abra [http://localhost:8000/docs](http://localhost:8000/docs).

3.  **Fluxo de Teste:**
    1.  **Registrar:** `POST /register` (crie um usuário com email).
    2.  **Login:** `POST /token` (copie o `access_token`).
    3.  **Autorizar:** Clique no cadeado no topo do Swagger e cole o token.
    4.  **Upload:** `POST /upload` (envie um vídeo MP4).
    5.  **Acompanhar:** `GET /status` (verifique o processamento).
    6.  **Download:** Use o link retornado no status para baixar o ZIP.

## ☸️ Kubernetes (Deploy)

Os manifestos para deploy em cluster (EKS/Kind) estão na pasta `k8s/`.

1.  **Infraestrutura:**
    ```bash
    kubectl apply -f k8s/infra/
    ```
2.  **Aplicações:**
    ```bash
    kubectl apply -f k8s/app/gateway/
    kubectl apply -f k8s/app/worker/
    ```

## 🧪 Testes e Qualidade

O projeto possui testes unitários cobrindo as Regras de Negócio (Use Cases).
Para rodar:
```bash
docker-compose exec gateway pytest
docker-compose exec worker pytest
```

## 🔄 CI/CD

Pipeline configurado no **GitHub Actions** (`.github/workflows/main.yml`) que executa:
1.  Instalação de dependências.
2.  Execução de testes unitários.
3.  Build das imagens Docker.