# AI Powered Question Generation System

This is an implementation of an AI powered system for question generation.

## Requirements

- Python 3.12.7 or later

## Installation
### Using Python & pip:
#### Create a new environment

```bash
$ python -m venv .venv
```

#### Activate the environment
```bash
# Linux / macOS (bash, zsh)
$ source .venv/bin/activate
# or
$ . .venv/bin/activate
```

```powershell
# Windows PowerShell
.venv\Scripts\Activate.ps1
# if blocked by execution policy (run once):
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Install dependencies
```bash
$ pip install -r src/requirements.txt
```

### Using UV:
```bash
$ uv sync
```
## Setup the environment variables

```bash
cp src/.env.example src/.env
```

Set your environment variables in `src/.env` (for example, `OPENAI_API_KEY`).

## Run Docker Compose Services

```bash
cd docker/env
cp .env.example.app .env.app
cp .env.example.mongodb .env.mongodb
cp .env.example.grafana .env.grafana
cp .env.example.mongodb-exporter .env.mongodb-exporter
```

- update the created files in `docker/env/` with your credentials

```bash
cd docker
sudo docker compose up -d
```
