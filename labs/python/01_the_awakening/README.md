# Lab P01 – The Awakening 🌅

A local mind comes online.
Microsoft Agent Framework + Docker Model Runner = no cloud, no limits.

---

### Goal

Run a **ChatAgent** fully offline using the **Microsoft Agent Framework**, connected to **Docker Model Runner (DMR)**.

> **UPDATE (08/10/2025):**
> 
> 💡 Inspired by Gisela Torres’s method posts and last video I just added a new approach. Everything can run in containers, app, model, and environment, thanks to Docker Compose and the Model Runner integration.
> 
> - Repo: https://github.com/0GiS0/docker-compose-ai-app
> - Video (in spanish): https://www.youtube.com/watch?v=_tM7dlhYWnY
>
> Greetings! 

> **NOTE 2:**
>
> You can review what I've learnt about Docker cagent here in [This repo](https://github.com/juangcarmona/cagent-playground)


### Setup

Make sure **Docker Model Runner** is enabled in Docker Desktop.
If you need GPU support, follow this guide: [Enable GPU for Docker Model Runner on Windows](https://jgcarmona.com/enable-gpu-docker-model-runner-windows/).

Create and activate your Python environment.
Requirements are listed in the **root `requirements.txt`** file.
Then, use the provided **VS Code launch configuration** to start the lab.

> ⚠️ A global `.env` as well as some particular `.env` files with sample variables are included for learning purposes only.
> In real products or repositories, environment variables should **never** be committed.

---

### Run

#### Local

Launch **Lab P01 – The Awakening** from the VS Code Run menu or press **F5**.

#### Docker Compose

Navigate to this folder and 
```
run docker compose up
```

---

> 🌒 *When machines wake locally, the cloud can rest.*
