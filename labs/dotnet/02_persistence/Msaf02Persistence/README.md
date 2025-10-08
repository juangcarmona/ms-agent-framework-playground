# Microsoft Agent Framework – Conversation Persistence PoC

A minimal proof-of-concept that demonstrates how to **persist multi-turn conversations** with the Microsoft Agent Framework (MAF) using **Entity Framework Core + PostgreSQL**. The API runs in **Docker**, supports **HTTPS**, and exposes a simple REST interface to create and manage conversations.

---

## 🧠 Overview

This project shows how to:

* Create and run **MAF ChatClient-based agents** locally.
* Store and retrieve conversation state (`AgentThread` serialized to JSON).
* Stream agent responses and persist all messages (user + assistant).
* Use **PostgreSQL** as the backing store for conversations.
* Configure **HTTPS** and **OpenAPI** documentation in a local container environment.

---

## 🧱 Project Structure

```
Msaf02Persistence/
├── Application/
│   ├── Models/
│   │   ├── ConversationResult.cs
│   │   └── StreamResult.cs
│   └── Services/
│       ├── AgentService.cs
│       └── ConversationService.cs
├── Controllers/
│   └── ConversationsController.cs
├── Domain/
│   ├── Entities/
│   │   ├── Conversation.cs
│   │   └── Message.cs
│   └── Repositories/
│       └── ConversationRepository.cs
├── Infrastructure/
│   └── ConversationDb.cs
├── docker-compose.yml
├── Dockerfile
├── Program.cs
└── appsettings.json
```

---

## 🚀 Run Locally with Docker Compose

### 1️⃣ Generate HTTPS certificate

This API uses HTTPS redirection. You must create a local dev certificate and export it:

```bash
# Create the target folder if missing
mkdir "$env:APPDATA\ASP.NET\Https" -Force

# Export a certificate (replace password if desired)
dotnet dev-certs https -ep "$env:APPDATA\ASP.NET\Https\Msaf02Persistence.pfx" -p YourCertPassword

# Trust it locally
dotnet dev-certs https --trust
```

Make sure your `docker-compose.override.yml` references it correctly:

```yaml
environment:
  - ASPNETCORE_Kestrel__Certificates__Default__Path=/home/app/.aspnet/https/Msaf02Persistence.pfx
  - ASPNETCORE_Kestrel__Certificates__Default__Password=YourCertPassword
volumes:
  - ${APPDATA}/ASP.NET/Https:/home/app/.aspnet/https:ro
```

---

### 2️⃣ Launch the stack

```bash
docker compose up --build
```

This spins up:

* **PostgreSQL** at `localhost:5432`
* **API** at:

  * HTTP → [http://localhost:5000/openapi](http://localhost:5000/openapi)
  * HTTPS → [https://localhost:5001/openapi](https://localhost:5001/openapi)

---

## 💾 Database Migrations

Migrations are auto-applied on container startup.
You can also run them manually:

```bash
dotnet ef migrations add InitialCreate -p Msaf02Persistence -s Msaf02Persistence
dotnet ef database update -p Msaf02Persistence -s Msaf02Persistence
```

---

## 🧩 API Endpoints

| Method | Endpoint                           | Description                        |
| ------ | ---------------------------------- | ---------------------------------- |
| GET    | `/api/conversations`               | List all conversations             |
| GET    | `/api/conversations/{id}`          | Get conversation details           |
| POST   | `/api/conversations`               | Create a new empty conversation    |
| POST   | `/api/conversations/{id}/messages` | Send a message and get AI response |

---

## 🧠 Architecture Notes

* **ConversationService** orchestrates message flow and persistence.
* **AgentService** encapsulates MAF agent creation and execution (streaming & non-streaming).
* **ConversationRepository** uses EF Core to persist entities.
* **PostgreSQL** connection string is injected via env vars or `appsettings.json`.

---

## 🧰 Environment Variables

| Variable                                              | Description                          | Default                                                    |
| ----------------------------------------------------- | ------------------------------------ | ---------------------------------------------------------- |
| `ConnectionStrings__DefaultConnection`                | PostgreSQL connection string         | `Host=db;Database=maf;Username=postgres;Password=postgres` |
| `OPENAI_API_KEY`                                      | Optional, for remote model endpoints | none                                                       |
| `ASPNETCORE_ENVIRONMENT`                              | Runtime environment                  | `Development`                                              |
| `ASPNETCORE_HTTP_PORTS`                               | HTTP port inside container           | `8080`                                                     |
| `ASPNETCORE_HTTPS_PORTS`                              | HTTPS port inside container          | `8081`                                                     |
| `ASPNETCORE_Kestrel__Certificates__Default__Path`     | Path to dev cert                     | `/home/app/.aspnet/https/Msaf02Persistence.pfx`            |
| `ASPNETCORE_Kestrel__Certificates__Default__Password` | Certificate password                 | `YourCertPassword`                                         |

---

## 📖 Next Steps

* Add streaming endpoint for live agent responses.
* Extend `ConversationService` to support conversation titles (auto-generated by agent).
* Add persistence for thread recovery (`AgentThread` JSON field).

---

## 🧩 Credits

Built with ❤️ using:

* Microsoft Agent Framework (Preview)
* Entity Framework Core
* ASP.NET Core 10
* PostgreSQL
* Docker Compose
