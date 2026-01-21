# Roteiro para Gravação do Vídeo de Apresentação - FIAP X

Este guia serve como um roteiro (script) técnico para a apresentação do projeto. O objetivo é demonstrar o domínio sobre os conceitos de **Clean Architecture**, **Microsserviços** e **Arquitetura Hexagonal**.

---

## ⏱️ Planejamento de Tempo (Total: ~7 minutos)

| Seção | Tempo Sugerido | Objetivo Principal |
| :--- | :--- | :--- |
| **1. Introdução** | 0:00 - 1:00 | Apresentar o problema e a solução macro. |
| **2. Arquitetura (Código)** | 1:00 - 3:30 | Mostrar a organização Clean Architecture e Portas/Adaptadores. |
| **3. Demonstração Prática** | 3:30 - 6:00 | Mostrar o fluxo: Registro -> Upload -> Processamento -> Download. |
| **4. Infra & CI/CD** | 6:00 - 7:00 | Mostrar Kubernetes e GitHub Actions. |

---

## 🎙️ Passo a Passo Detalhado

### 1. Introdução (Contexto)
- **O que falar:** "O desafio da FIAP X consistia em transformar um sistema legado monolítico em uma solução de microsserviços moderna, resiliente e escalável."
- **O que mostrar:** O diagrama **Mermaid** no `README.md` principal.
- **Destaque:** Mencione o uso de mensageria assíncrona com **RabbitMQ** para evitar perda de dados em picos de tráfego.

### 2. Mergulho na Arquitetura (O Coração do Projeto)
*Abra o VS Code e navegue pelas pastas:*

- **Domínio (Domain):**
    - Caminho: `app/gateway/src/domain/entities.py`
    - **Falar:** "Começamos pelo Domínio. Aqui temos Entidades puras como `User` e `Video`. Elas contêm apenas a lógica de negócio e não dependem de frameworks externos."
- **Portas (Ports/Interfaces):**
    - Caminho: `app/gateway/src/ports/interfaces.py`
    - **Falar:** "Seguindo a Arquitetura Hexagonal, definimos **Ports**. São interfaces que ditam o que o sistema precisa (como persistir um vídeo ou enviar uma notificação), sem saber como isso será feito."
- **Casos de Uso (Use Cases):**
    - Caminho: `app/worker/src/use_cases/process_video.py`
    - **Falar:** "Os Casos de Uso orquestram a regra de negócio. Eles usam as interfaces das Portas. Isso nos permite testar toda a lógica do Worker sem precisar de um banco de dados real ou internet."
- **Adaptadores (Adapters):**
    - Caminho: `app/gateway/src/adapters/`
    - **Falar:** "Os Adaptadores são as implementações técnicas. Temos aqui o `PostgresUserRepository` para banco de dados e o `SESNotificationService` para a AWS. Graças às Portas, podemos trocar o provedor de e-mail ou o banco de dados sem alterar uma linha da lógica de negócio."

### 3. Demonstração ao Vivo (End-to-End)
*Mostre o terminal com os containers rodando e o Postman ou Swagger:*

1.  **Registro:** Mostre o envio do JSON com `username`, `email` e `password`.
2.  **Login:** Obtenha o Token JWT.
3.  **Upload:** Envie um vídeo `.mp4`.
4.  **Worker em Ação:** Mostre os logs do Docker (`docker-compose logs -f worker`). Explique: "O Worker detectou a mensagem no RabbitMQ, baixou o vídeo do volume compartilhado e está usando **OpenCV** para extrair os frames."
5.  **Cache com Redis:** No `GET /status`, mencione: "A resposta é instantânea porque estamos usando o **Redis** como camada de cache para o status dos vídeos."

### 4. Infraestrutura e Qualidade
- **Kubernetes:** Mostre a pasta `k8s/`. Explique o uso de **StatefulSets** para o banco e **HPA** para escalabilidade automática dos pods na AWS.
- **CI/CD:** Mostre o `.github/workflows/main.yml`. Explique que cada commit passa por testes unitários antes de gerar a imagem Docker.

### 5. Conclusão
- **Falar:** "Esta arquitetura garante que a FIAP X tenha um sistema pronto para crescer, fácil de testar e totalmente preparado para o ambiente de nuvem da AWS."

---

## 💡 Dicas Adicionais
- **Fonte do VS Code:** Aumente um pouco (Ctrl +) para que fique legível no vídeo.
- **Ambiente Limpo:** Certifique-se de que o banco de dados esteja limpo antes de começar a gravação.
- **Objetividade:** Se o processamento do vídeo for demorar, corte o vídeo ou pause a gravação e volte quando o status for `COMPLETED`.
